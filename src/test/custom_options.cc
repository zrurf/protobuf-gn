// Copyright 2023 The Fuchsia Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "gtest/gtest.h"
#include "third_party/protobuf/test/custom_options.pb.h"

namespace {
TEST(CustomOptions, MessageOption) {
  EXPECT_EQ("Hello world!",
            MyMessage::descriptor()->options().GetExtension(my_option));
}
}  // namespace
