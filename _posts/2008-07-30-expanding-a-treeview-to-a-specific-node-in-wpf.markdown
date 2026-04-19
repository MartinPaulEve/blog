---
layout: post
image: 
    feature: geek.png
status: publish
published: true
title: Expanding a treeview to a specific node in WPF
wordpress_id: 251
wordpress_url: http://pro.grammatic.org/post-expanding-a-treeview-to-a-specific-node-in-wpf-51.aspx
date: !binary |-
  MjAwOC0wNy0zMCAxMzo0MDo1NSArMDIwMA==
date_gmt: !binary |-
  MjAwOC0wNy0zMCAxMzo0MDo1NSArMDIwMA==
categories:
- Technology
- .NET
tags:
- C#
- WPF
comments: []
doi: "https://doi.org/10.59348/ewvkq-hcr13"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2008/07/30/expanding-a-treeview-to-a-specific-node-in-wpf"
---
<p>I've been exploring the dark alleyways of the Windows Presentation Foundation this week and found no way in my trawlings of the net to expand a treeview to a specific node.</p>
<p>No FindNode, no ExpandTo or ExpandAll. Great.</p>
<p>Anyway, here's the solution I came up with. It relies upon a binding the Tag property to the text you are searching for, but that could obviously be changed.</p>

{% highlight csharp %}
        /// <summary>
        /// Expand a TreeView to a specific node
        /// </summary>
        /// <param name="tv">The treeview</param>
        /// <param name="node">The string of the node in the Item.Tag property to expand to</param>
        void jumpToFolder(TreeView tv, string node)
        {
            bool done = false;
            ItemCollection ic = tv.Items;

            while (!done)
            {
                bool found = false;

                foreach (TreeViewItem tvi in ic)
                {    
                    if (node.StartsWith(tvi.Tag.ToString()))
                    {
                        found = true;
                        tvi.IsExpanded = true;
                        ic = tvi.Items;
                        if (node == tvi.Tag.ToString()) done = true;
                        break;
                    }
                }

                done = (found == false && done == false);
            }
        }
{% endhighlight %}





