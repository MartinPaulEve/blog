---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2022/07/28/lastpass-cli-cant-login-using-master-password
date: 2022-07-28
doi: https://doi.org/10.59348/bw3a9-cm163
roguescholar: https://rogue-scholar.org/records/k6zf9-cbf10
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lyufbys2r
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
title: Lastpass CLI can't login using master password
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lyufbys2r"
categories:
- Information Security
kcworks: https://works.hcommons.org/records/v24hk-gax30
---

If you can't login using the Lastpass CLI tool and it just says "unknown" when you enter your password, there's [a simple fix](https://github.com/lastpass/lastpass-cli/issues/604).

Go to My Vault -> Account Settings.

In there, press "Show Advanced Settings".

Then set "Password Iterations" to 100100 and follow the procedure.

After that, the CLI tool will work again!