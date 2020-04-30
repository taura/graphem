#!/usr/bin/python

import sys
import xml.sax

def is_layer_node(name, attrs):
    if name != "g": return 0
    if attrs.get("inkscape:groupmode") != "layer": return 0
    return 1

class LayerHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.layers = []
    def startElement(self, name, attrs):
        if is_layer_node(name, attrs):
            self.layers.append(attrs["id"])

def get_layers(svg_file):
    parser = xml.sax.make_parser()
    handler = LayerHandler()
    parser.setContentHandler(handler)
    parser.parse(svg_file)
    return handler.layers

def num_layers(svg_file):
    layers = get_layers(svg_file)
    return len(layers)

def id_of_nth_layer(svg_file, n):
    layers = get_layers(svg_file)
    if n > 0 and n - 1 < len(layers):
        return layers[n - 1]
    else:
        return None

def main():
    # sys.stderr.write("%s\n" % sys.argv)
    l = len(sys.argv)
    if l == 1:
        p = sys.argv[0]
        sys.stderr.write(r"""usage: 
  %s num svg_file
  %s check svg_file n output
  %s id svg_file n
""" % (p, p, p))
        return 1
    else:
        cmd = sys.argv[1]
        if cmd == "num":
            svg_file = sys.argv[2]
            print num_layers(svg_file)
            return 0
        elif cmd == "check":
            svg_file = sys.argv[2]
            n = int(sys.argv[3])
            name = id_of_nth_layer(svg_file, n)
            if name is None:
                return 1
            else:
                print sys.argv[4]
                return 0
        elif cmd == "id":
            svg_file = sys.argv[2]
            n = int(sys.argv[3])
            name = id_of_nth_layer(svg_file, n)
            if name is None:
                return 1
            else:
                print name
                return 0
        else:
            assert 0,cmd

sys.exit(main())






