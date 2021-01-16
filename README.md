# Protocol Buffers GN Build Support

This repository contains
[GN build system](https://gn.googlesource.com/gn/+/HEAD/) support for
[Protocol Buffers](https://github.com/protocolbuffers/protobuf). It's in its own
repository because it needs to be shared by
[Fuchsia](https://fuchsia.googlesource.com/fuchsia/) and
[Cobalt](https://fuchsia.googlesource.com/cobalt/).

This repo should be checked out in secondary build directory that corresponds to
the location of the protobuf repo. See the
[GN documentation on secondary_source](https://gn.googlesource.com/gn/+/master/docs/reference.md#other-help-topics-gn-file-variables).

For example if `//.gn` contains:

```gn
secondary_source = "//build/secondary/"
```

And protobuf is checked out at `//third_party/protobuf`, then this repo should
be checked out at `//build/secondary/third_party/protobuf`.
