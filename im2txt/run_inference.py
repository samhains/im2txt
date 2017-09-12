# Copyright 2016 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
r"""Generate captions for images using default beam search parameters."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from PIL import Image

import google_scraper
import math
import os
import random
import json


import tensorflow as tf

import os, shutil
from im2txt import configuration
from im2txt import inference_wrapper
from im2txt.inference_utils import caption_generator
from im2txt.inference_utils import vocabulary

FLAGS = tf.flags.FLAGS

tf.flags.DEFINE_string("checkpoint_path", "",
                       "Model checkpoint file or directory containing a "
                       "model checkpoint file.")
tf.flags.DEFINE_string("vocab_file", "", "Text file containing the vocabulary.")
tf.flags.DEFINE_string("input_files", "",
                       "File pattern or comma-separated list of file patterns "
                       "of image files.")

tf.logging.set_verbosity(tf.logging.INFO)

def delete_files(folder):
  for the_file in os.listdir(folder):
      file_path = os.path.join(folder, the_file)
      try:
          if os.path.isfile(file_path):
              os.unlink(file_path)
          #elif os.path.isdir(file_path): shutil.rmtree(file_path)
      except Exception as e:
          print(e)

def get_filenames():
  filenames = []
  for file_pattern in FLAGS.input_files.split(","):
    filenames.extend(tf.gfile.Glob(file_pattern))
  tf.logging.info("Running caption generation on %d files matching %s",
                  len(filenames), FLAGS.input_files)
  return filenames


def main(_):
  # Build the inference graph.
  g = tf.Graph()
  with g.as_default():
    model = inference_wrapper.InferenceWrapper()
    restore_fn = model.build_graph_from_config(configuration.ModelConfig(),
                                               FLAGS.checkpoint_path)
  g.finalize()

  # Create the vocabulary.
  vocab = vocabulary.Vocabulary(FLAGS.vocab_file)



  with tf.Session(graph=g) as sess:
    # Load the model from checkpoint.
    restore_fn(sess)

    # Prepare the caption generator. Here we are implicitly using the default
    # beam search parameters. See caption_generator.py for a description of the
    # available beam search parameters.

    caption = caption_to_img(sess, vocab, model, 'genesis')
    print("CAPTION", caption)
    while True:
      caption = caption_to_img(sess, vocab, model, caption)
      print("CAPTION", caption)
    # caption_to_img(sess, vocab, model, caption)


def caption_to_img(sess, vocab, model, caption):
    google_scraper.main(caption)
    filenames = get_filenames()
    generator = caption_generator.CaptionGenerator(model, vocab)
    caption = generate_captions(sess, generator, vocab, filenames)
    delete_files('./im2txt/images/')
    print(caption)
    return caption

def generate_captions(sess, generator, vocab, filenames):
    data = {}
    for filename in filenames:

      with tf.gfile.GFile(filename, "r") as f:
        image = f.read()
      captions = generator.beam_search(sess, image)
      key = os.path.basename(filename)

      caption = captions[0]
      sentence = [vocab.id_to_word(w) for w in caption.sentence[1:-1]]
      sentence = " ".join(sentence)
      sentence = sentence[2].upper() + sentence[3:]
      if (sentence.startswith("Bunch of") or sentence.startswith("Group of")):
          sentence = sentence[9].upper() + sentence[10:]
      if (sentence.startswith("Close up of") and random.random() > 0.5):
          sentence = sentence[12].upper() + sentence[13:]
      if (sentence.endswith(".")):
          sentence = sentence[:-1]

      return sentence
      # data[key] = sentence
      # print("  %d) %s (p=%f)" % (0, sentence, math.exp(caption.logprob)))
      # with open('data.json', 'w') as outfile:
          # json.dump(data, outfile)

if __name__ == "__main__":
  tf.app.run()
