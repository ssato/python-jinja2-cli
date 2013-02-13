"""
 :copyright: (c) 2012 by Satoru SATOH <ssato@redhat.com>
 :license: BSD-3

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions are met:

   * Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.
   * Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.
   * Neither the name of the author nor the names of its contributors may
     be used to endorse or promote products derived from this software
     without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
 DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

def is_dict(x):
    return isinstance(x, (MyDict, dict))


def is_iterable(x):
    return isinstance(x, (list, tuple)) or getattr(x, "next", False)


class MyDict(dict):

    @classmethod
    def createFromDict(cls, dic={}):
        md = MyDict()

        for k, v in dic.iteritems():
            md[k] = cls.createFromDict(v) if is_dict(v) else v

        return md

    def update(self, other, merge_lists=False):
        """Merge `self` and `other` recursively.

        :param merge_lists: Merge not only dicts but also lists,
            e.g. [1, 2], [3, 4] ==> [1, 2, 3, 4]
        """
        if is_dict(other):
            for k, v in other.iteritems():
                if k in self and is_dict(v) and is_dict(self[k]):
                    self[k].update(v, merge_lists)  # update recursively.
                else:
                    if merge_lists and is_iterable(v):
                        self[k] = self[k] + list(v)  # append v :: list
                    else:
                        self[k] = v  # replace self[k] w/ v or set.


# vim:sw=4:ts=4:et: