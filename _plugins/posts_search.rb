# Whole-archive full-text search for /posts/.
#
# The archive page already carries every post's title and excerpt, so the
# client only needs to know *which* posts contain the words typed. Rather
# than ship every post's text (1.3MB gzipped) or even each post's unique
# words (680KB), the build emits a single inverted index at
# /posts/search.json (plus a pregzipped .json.gz twin, ~400KB): the posts'
# URLs in order and, for every distinct word in any post, the gap-encoded
# positions of the posts that contain it. posts-search.js fetches it on the
# first keystroke, matches each query term as a substring of the vocabulary,
# ORs the posting lists per term and ANDs across terms, then simply hides
# the archive entries that did not match.
#
# The PostsSearch module holds the pure builders (no Jekyll dependency) so
# they can be unit-tested; the :post_write hook feeds it the rendered posts.

require "cgi"
require "fileutils"
require "json"
require "zlib"

module PostsSearch
  BASE_DIR = "posts".freeze
  FILE_NAME = "search.json".freeze
  MIN_LENGTH = 2

  # HTML 4's Latin-1 named entities (U+00C0..U+00FF, in code point order)
  # on top of the five CGI.unescapeHTML knows: these are the letters that
  # survive in rendered posts (caf&eacute;, Z&uuml;rich). Any other named
  # entity is treated as a word break rather than being glued into a word.
  LATIN1_NAMES = %w[
    Agrave Aacute Acirc Atilde Auml Aring AElig Ccedil Egrave Eacute Ecirc
    Euml Igrave Iacute Icirc Iuml ETH Ntilde Ograve Oacute Ocirc Otilde Ouml
    times Oslash Ugrave Uacute Ucirc Uuml Yacute THORN szlig agrave aacute
    acirc atilde auml aring aelig ccedil egrave eacute ecirc euml igrave
    iacute icirc iuml eth ntilde ograve oacute ocirc otilde ouml divide
    oslash ugrave uacute ucirc uuml yacute thorn yuml
  ].freeze
  ENTITIES = LATIN1_NAMES.each_with_index.to_h { |name, i| [name, (0xC0 + i).chr(Encoding::UTF_8)] }
    .merge("nbsp" => " ", "amp" => "&", "lt" => "<", "gt" => ">",
           "quot" => '"', "apos" => "'").freeze

  # Strip <script>/<style> wholesale (their bodies are code, not prose),
  # then every other tag, then decode entities.
  def self.text_of(html)
    text = html.to_s.gsub(%r{<(script|style)\b[^>]*>.*?</\1\s*>}mi, " ")
    text = text.gsub(/<[^>]+>/, " ")
    text = text.gsub(/&([a-zA-Z][a-zA-Z0-9]*);/) { ENTITIES.fetch($1, " ") }
    CGI.unescapeHTML(text)
  end

  # Unique, sorted, lowercased Unicode words of at least MIN_LENGTH
  # characters. The query side (posts-search.js) tokenises identically.
  def self.words(html)
    text_of(html).downcase.scan(/[\p{L}\p{N}]+/)
      .select { |word| word.length >= MIN_LENGTH }
      .uniq.sort
  end

  # [0, 1, 5, 6] -> [0, 0, 3, 0]: each position as its gap from the
  # previous one, which keeps the posting lists mostly tiny numbers.
  def self.delta_encode(indices)
    previous = -1
    indices.map do |index|
      gap = index - previous - 1
      previous = index
      gap
    end
  end

  # posts: [{"url", "title", "content"}] in display order.
  # => {"u" => [urls], "w" => {word => [gap-encoded post positions]}}
  def self.build_index(posts)
    postings = Hash.new { |hash, key| hash[key] = [] }
    urls = []
    (posts || []).each_with_index do |post, position|
      urls << post["url"].to_s
      words("#{post['title']} #{post['content']}").each do |word|
        postings[word] << position
      end
    end
    encoded = postings.keys.sort.each_with_object({}) do |word, hash|
      hash[word] = delta_encode(postings[word])
    end
    { "u" => urls, "w" => encoded }
  end
end

if defined?(Jekyll)
  # The posts' rendered bodies only exist once the site has been rendered,
  # so the index is written straight into the destination after the write
  # pass. mtime 0 keeps the gzip bytes stable across identical builds.
  Jekyll::Hooks.register :site, :post_write do |site|
    posts = site.posts.docs.reverse.map do |doc|
      { "url" => doc.url, "title" => doc.data["title"], "content" => doc.content }
    end
    target = File.join(site.dest, PostsSearch::BASE_DIR, PostsSearch::FILE_NAME)
    FileUtils.mkdir_p(File.dirname(target))
    json = JSON.generate(PostsSearch.build_index(posts))
    File.write(target, json)
    Zlib::GzipWriter.open("#{target}.gz") do |gz|
      gz.mtime = 0
      gz.write(json)
    end
  end
end
