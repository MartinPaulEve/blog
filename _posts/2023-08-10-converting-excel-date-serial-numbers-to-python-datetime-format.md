---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2023/08/10/converting-excel-date-serial-numbers-to-python-datetime-format
date: 2023-08-10
doi: https://doi.org/10.59348/dbrja-s7w36
roguescholar: https://rogue-scholar.org/records/1ghtn-zjs56
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7ly34f5x2i
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
title: Converting Excel date serial numbers to Python datetime format
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7ly34f5x2i"
categories:
- Programming
---

Excel stores dates in a very odd way: a serial number of days since 1900.

To convert an Excel datestamp to a Python datetime object, you can use this function:

	def date_serial_number(serial_number: int) -> datetime:
	    """
	    Convert an Excel serial number to a Python datetime object
	    :param serial_number: the date serial number
	    :return: a datetime object
	    """
	    # Excel stores dates as "number of days since 1900"
	    import datetime as dt

	    delta = dt.datetime(1899, 12, 30) + dt.timedelta(days=serial_number)
	    return delta

Hope this helps someone.