from __future__ import absolute_import

import sys

from .xml import ElementTree as ET
from .constants import disa_cciuri, XCCDF11_NS, stig_ns, stig_refs

def add_references(reference, destination):
    try:
        reference_root = ET.parse(reference)
    except IOError as exception:
        print("INFO: DISA STIG Reference file not found for this platform")
        sys.exit(0)

    reference_rules = reference_root.findall('.//{%s}Rule' % XCCDF11_NS)

    dictionary = {}

    for rule in reference_rules:
        version = rule.find('.//{%s}version' % XCCDF11_NS)
        if version is not None and version.text:
            dictionary[version.text] = rule.get('id')

    target_root = ET.parse(destination)
    target_rules = target_root.findall('.//{%s}Rule' % XCCDF11_NS)

    for rule in target_rules:
        refs = rule.findall('.//{%s}reference' % XCCDF11_NS)
        for ref in refs:
            if (ref.get('href').startswith(stig_refs) and
                    ref.text in dictionary):
                index = rule.getchildren().index(ref)
                new_ref = ET.Element(
                    '{%s}reference' % XCCDF11_NS, {'href': stig_ns})
                new_ref.text = dictionary[ref.text]
                new_ref.tail = ref.tail
                rule.insert(index + 1, new_ref)

    return target_root
