#!/usr/bin/env python -*- coding: utf-8 -*-

def remove_tags(text):
  """ Removes <tags> in angled brackets from text. """
  import re
  tags = {i:" " for i in re.findall("(<[^>\n]*>)",text.strip())}
  no_tag_text = reduce(lambda x, kv:x.replace(*kv), tags.iteritems(), text)
  return " ".join(no_tag_text.split())