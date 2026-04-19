---
layout: post
image: 
    feature: geek.png
status: publish
published: true
title: Handling the absence of a (newline) break tag in JATS
wordpress_id: 2985
wordpress_url: https://www.martineve.com/?p=2985
date: !binary |-
  MjAxNC0wMS0xMyAxODo1NjozOSArMDEwMA==
date_gmt: !binary |-
  MjAxNC0wMS0xMyAxODo1NjozOSArMDEwMA==
categories:
- Academia
- meTypeset
tags:
- meTypeset
comments: []
doi: "https://doi.org/10.59348/485d3-zd498"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2014/01/13/handling-the-absence-of-a-newline-break-tag-in-jats"
---
<p>As I noted in a previous post, a lot of my work this term involves technical implementation of an open source JATS (previously NLM) typesetter for scholarly articles. What this means is that I am writing a system that takes imperfectly formatted Microsoft Word documents and transforms them into an XML format that we can use to produce HTML, PDFs, EPUBs you name it. I'm intending to write about my experience of developing this system as a way of ensuring my thoughts are clear but also as a way in for anybody else who might ever want to understand the meTypeset codebase.</p>
<p>One of the problems that I dealt with today is the fact that the JATS standard does not allow for a line-break to occur mid-way through a paragraph. This will occur in a Word document when the user types a paragraph and then presses control + enter. So it isn't a new paragraph, it instead is just a new line within a paragraph. In XHTML this would be presented like this:</p>

{% highlight html %}
<p>A line of text<br/>another line of text</p>
{% endhighlight %}

<p>JATS has no equivalent to the br tag mid-way through that line.</p>
<p>The way that I've decided to handle this in meTypeset is via an option flag in the configuration file: &lt;mt:linebreaks-as-comments&gt;False&lt;/mt:linebreaks-as-comments&gt;</p>
<p>When this is set to True, meTypeset inserts a commented-out variable that indicates to subsequent transforms that they should insert a line-break here to ensure fidelity to the original document. The comment tag is &lt;!--meTypeset:br--&gt;.</p>
<p>When this is set to False, we treat the &lt;!--meTypeset:br--&gt; tags as though they should be changed into a &lt;/p&gt;&lt;p&gt; sequence (close-paragraph, open-paragraph).</p>
<p>This sounds simple, but there are some dangerous problems. Consider what happens in this scenario:</p>

{% highlight html %}
<p>A line of text<!--meTypeset:br-->another line of tex</p>
{% endhighlight %}

<p>If you just transform that &lt;!--meTypeset:br--&gt; into a &lt;/p&gt;&lt;p&gt;, you get a hideously malformed mess that looks like this:</p>

{% highlight html %}
<p>A line of <italic>text</p><p>another</italic> line of text</p>
{% endhighlight %}

<p>So, what we have to do is to build a stack of all the elements applied to the tail after the comment() element in that XPath. This is implemented in <a href="https://github.com/MartinPaulEve/meTypeset/blob/fb11e34126493e0bf2b95681b558dd246fc6df38/bin/nlmmanipulate.py">our NLMManipulator class</a>.</p>
<p>The relevant method that styles this is handle_nested_elements:</p>

{% highlight python %}
    @staticmethod
    def handle_nested_elements(iter_node, move_node, node, node_parent, outer_node, tag_name, tail_stack,
                               tail_stack_objects):
        while iter_node.tag != tag_name:
            tail_stack.append(iter_node.tag)
            tail_stack_objects.append(iter_node)
            iter_node = iter_node.getparent()

        # get the tail (of the comment) and style it
        append_location = None
        tail_text = node.tail
        iterator = 0
        tail_stack.reverse()
        tail_stack_objects.reverse()
        # rebuild the styled tree on a set of subelements
        for node_to_add in tail_stack:
            sub_element = etree.Element(node_to_add)
            if iterator == len(tail_stack) - 1:
                sub_element.text = node.tail

            if iterator == 0:
                outer_node = sub_element

            iterator += 1
            if append_location is None:
                tail_stack_objects[0].addnext(sub_element)
                append_location = sub_element
            else:
                append_location.append(sub_element)
                append_location = sub_element

        # remove the old node (this is in the element above)
        node.getparent().remove(node)
        # set the search node to the outermost node so that we can find siblings
        node_parent = iter_node
        node = outer_node
        move_node = True
        return move_node, node, node_parent
{% endhighlight %}

<p>This builds a list of elements working outwards before re-adding the content of the tail of the last processed node using lxml.</p>
<p>Combined with the search_and_copy and process_node_for_tags method, this has worked in the limited cases that I've thrown at it. I'm sure there are bugs to be uncovered, but this is the start of our handling of this scenario.</p>





