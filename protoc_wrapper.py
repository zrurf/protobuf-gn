#!/usr/bin/env python3.8
# Copyright 2012 Google Inc.  All Rights Reserved.

"""
A simple wrapper for protoc.
Script for //third_party/protobuf/proto_library.gni .
Features:
- Inserts #include for extra header automatically.
- Prevents bad proto names.
"""

from __future__ import print_function
import argparse
import os.path
import subprocess
import sys
import tempfile

PROTOC_INCLUDE_POINT = "// @@protoc_insertion_point(includes)"


def FormatGeneratorOptions(options):
  if not options:
    return ""
  if options.endswith(":"):
    return options
  return options + ":"


def VerifyProtoNames(protos):
  for filename in protos:
    if "-" in filename:
      raise RuntimeError("Proto file names must not contain hyphens "
                         "(see http://crbug.com/386125 for more information).")


def StripProtoExtension(filename):
  if not filename.endswith(".proto"):
    raise RuntimeError("Invalid proto filename extension: "
                       "{0} .".format(filename))
  return filename.rsplit(".", 1)[0]


def WriteIncludes(headers, include):
  for filename in headers:
    include_point_found = False
    contents = []
    with open(filename) as f:
      for line in f:
        stripped_line = line.strip()
        contents.append(stripped_line)
        if stripped_line == PROTOC_INCLUDE_POINT:
          if include_point_found:
            raise RuntimeError("Multiple include points found.")
          include_point_found = True
          extra_statement = "#include \"{0}\"".format(include)
          contents.append(extra_statement)

      if not include_point_found:
        raise RuntimeError("Include point not found in header: "
                           "{0} .".format(filename))

    with open(filename, "w") as f:
      for line in contents:
        print(line, file=f)


def WritePluginDepfile(depfile, outputs, dependencies):
  with open(outputs) as f:
    outs = " ".join(line.strip() for line in f)
  with open(dependencies) as f:
    deps = " ".join(line.strip() for line in f)
  with open(depfile, 'w') as f:
    print("{0}: {1}".format(outs, deps), file=f)


def main(argv):
  parser = argparse.ArgumentParser()
  parser.add_argument("--protoc",
                      help="Relative path to compiler.")

  parser.add_argument("--proto-in-dir",
                      help="Base directory with source protos.")
  parser.add_argument("--cc-out-dir",
                      help="Output directory for standard C++ generator.")
  parser.add_argument("--py-out-dir",
                      help="Output directory for standard Python generator.")
  parser.add_argument("--plugin-out-dir",
                      help="Output directory for custom generator plugin.")

  parser.add_argument("--plugin",
                      help="Relative path to custom generator plugin.")
  parser.add_argument("--plugin-depfile",
                      help="Output location for the plugin depfile.")
  parser.add_argument("--plugin-depfile-deps",
                      help="File containing plugin deps not set as other input.")
  parser.add_argument("--plugin-depfile-outputs",
                      help="File containing a list of files that will be generated.")
  parser.add_argument("--plugin-options",
                      help="Custom generator plugin options.")
  parser.add_argument("--cc-options",
                      help="Standard C++ generator options.")
  parser.add_argument("--include",
                      help="Name of include to insert into generated headers.")
  parser.add_argument("--import-dir", action="append", default=[],
                      help="Extra import directory for protos, can be repeated."
  )
  parser.add_argument("--descriptor-set-out",
                      help="Passed through to protoc as --descriptor_set_out")

  parser.add_argument("protos", nargs="+",
                      help="Input protobuf definition file(s).")

  options = parser.parse_args()

  proto_dir = os.path.relpath(options.proto_in_dir)
  protoc_cmd = [os.path.realpath(options.protoc)]

  protos = options.protos
  headers = []
  VerifyProtoNames(protos)

  if options.descriptor_set_out:
    protoc_cmd += ["--descriptor_set_out", options.descriptor_set_out]

  if options.py_out_dir:
    protoc_cmd += ["--python_out", options.py_out_dir]

  if options.cc_out_dir:
    cc_out_dir = options.cc_out_dir
    cc_options = FormatGeneratorOptions(options.cc_options)
    protoc_cmd += ["--cpp_out", cc_options + cc_out_dir]
    for filename in protos:
      stripped_name = StripProtoExtension(filename)
      headers.append(os.path.join(cc_out_dir, stripped_name + ".pb.h"))

  if options.plugin_out_dir:
    plugin_options = FormatGeneratorOptions(options.plugin_options)
    protoc_cmd += [
      "--plugin", "protoc-gen-plugin=" + os.path.relpath(options.plugin),
      "--plugin_out", plugin_options + options.plugin_out_dir
    ]

  if options.plugin_depfile:
    if not options.plugin_depfile_deps or not options.plugin_depfile_outputs:
      raise RuntimeError("If plugin depfile is supplied, then the plugin "
                         "depfile deps and outputs must be set.")
    depfile = options.plugin_depfile
    dep_info = options.plugin_depfile_deps
    outputs = options.plugin_depfile_outputs
    WritePluginDepfile(depfile, outputs, dep_info)

  protoc_cmd += ["--proto_path", proto_dir]
  for path in options.import_dir:
    protoc_cmd += ["--proto_path", path]

  protoc_cmd += [os.path.join(proto_dir, name) for name in protos]

  ret = subprocess.call(protoc_cmd)
  if ret != 0:
    raise RuntimeError("Protoc has returned non-zero status: "
                       "{0} .".format(ret))

  if options.include:
    WriteIncludes(headers, options.include)


if __name__ == "__main__":
  try:
    main(sys.argv)
  except RuntimeError as e:
    print(e, file=sys.stderr)
    sys.exit(1)
