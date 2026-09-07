# Surfaces a failed Last.fm fetch in the build output. The deploy pipeline
# treats the fetch as a tolerant step (stale listening stats must never block
# a deploy), so fetch_lastfm.py records failures in _lastfm/fetch_error.json
# and this plugin reports them on every build until a fetch succeeds again —
# otherwise the only symptom would be a silently stale sidebar widget.
#
# LastfmCheck holds the pure logic (no Jekyll dependency) so it can be
# unit-tested in isolation; the hook below wires it into the build.

require "json"

module LastfmCheck
  SENTINEL = "_lastfm/fetch_error.json".freeze

  # A human-readable error for the build log, or nil when the last fetch
  # succeeded (no sentinel on disk). A corrupt sentinel still reports the
  # failure — it must never crash the build.
  def self.error_message(root)
    path = File.join(root, SENTINEL)
    return nil unless File.file?(path)
    begin
      record = JSON.parse(File.read(path))
      "last fetch failed at #{record['at']}: #{record['error']} " \
        "(the sidebar widget is serving stale data)"
    rescue JSON::ParserError
      "last fetch failed (#{SENTINEL} is unreadable); " \
        "the sidebar widget is serving stale data"
    end
  end
end

if defined?(Jekyll)
  Jekyll::Hooks.register :site, :after_init do |site|
    message = LastfmCheck.error_message(site.source)
    Jekyll.logger.error("Last.fm:", message) if message
  end
end
