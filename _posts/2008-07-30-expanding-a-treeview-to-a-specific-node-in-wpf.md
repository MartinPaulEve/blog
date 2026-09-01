---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2008/07/30/expanding-a-treeview-to-a-specific-node-in-wpf
categories:
- Programming
comments: []
date: 2008-07-30 13:40:55 +0200
date_gmt: 2008-07-30 13:40:55 +0200
doi: https://doi.org/10.59348/ewvkq-hcr13
roguescholar: https://rogue-scholar.org/records/hynw8-4zy43
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mmpxmax2t
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- C#
- WPF
title: Expanding a treeview to a specific node in WPF
wordpress_id: 251
wordpress_url: http://pro.grammatic.org/post-expanding-a-treeview-to-a-specific-node-in-wpf-51.aspx
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mmpxmax2t"
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