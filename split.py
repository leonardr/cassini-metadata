# Parse a consolidated label file derived from the Cassini ISS Online
# Data Volumes.
from pdb import set_trace
import json
import os

# consolidated.lbl was generated with this shell command:
# for i in `find -name *.LBL`; do echo $i >> consolidated.lbl; cat $i >> consolidated.lbl; done
input_file = "consolidated.lbl"
output_template = '%s.ndjson'

class Object(dict):

    def __init__(self):
        self.children = []

    @property
    def jsonable(self):
        x = dict(self)
        if self.children:
            x['_children'] = [c.jsonable for c in self.children]
        return x

class Record(Object):

    def __init__(self, filename):
        super(Record, self).__init__()
        self.original_filename = filename
        filename = filename[2:]
        volume, ignore, group, label = filename.split("/")
        self['_volume'] = volume
        self['_group'] = group
        self['_label_file'] = label

class Parser(object):

    def __init__(self):
        self.seen = set()
        self.current_record = None
        self.object_stack = []
        self.outputs = {}
        self.count = 0
        self.previous_key = None
        self.previous_line = None
        
    def parse(self, fh):
        """Parse a number of labels concatenated into a single file."""
        for line in fh:
            original_line = line
            line = line.strip()
            if not line:
                # Blank
                continue
            if line.startswith("/*"):
                # Comment
                continue
            if line == 'END':
                self.output_current_record()
                continue
            if line.startswith("./"):
                # Brand new record.
                if self.current_record:
                    # The previous record was empty, either because of
                    # an I/O error during the find command or while
                    # the tarball was being un-tarred. Read the file
                    # from disk -- hopefully it's either there now or it has
                    # been manually replaced.
                    f = self.current_record.original_filename
                    lines = open(self.current_record.original_filename).readlines()
                    if lines:
                        self.parse(lines)
                        self.current_record = Record(line)
                    else:
                        print("%s is empty and needs to be fixed from the tarball." % f)
                        self.current_record = None
                        self.object_stack = []
                # Start a new Record and treat this line as the filename.
                self.current_record = Record(line)
                self.object_stack.append(self.current_record)
                continue

            if line.startswith("END_OBJECT = "):
                ignored = self.object_stack.pop()
                continue

            obj = self.object_stack[-1]
            res = [x.strip() for x in line.split("=", 1)]
            if len(res) == 2:
                key, value = res
                self.previous_key = key
                obj[key] = self.process_value(value)
            elif self.previous_key:
                # This line is the continuation of the previous line.
                # This is very rare, but it does happen.                    
                obj[self.previous_key] = self.process_value(
                    obj[self.previous_key] + ' ' + value
                )

            if key == 'OBJECT':
                child = Object()
                self.current_record.children.append(child)
                child['_type'] = self.process_value(value)
                self.object_stack.append(child)
                continue
            if not value:
                unresolved_key = key
                continue
            self.object_stack[-1][key] = self.process_value(value)

    def process_value(self, value):
        if not value:
            return value
        if value[0] == '"' and value[-1] == '"':
            return value[1:-1]
        try:
            if '.' in value:
                value = float(value)
            else:
                value = int(value)
        except ValueError:
            pass
        return value            
            
    def output_current_record(self):
        assert [self.current_record] == self.object_stack
        key = self.current_record['_label_file']
        if key in self.seen:
            print ("Already processed a %s, ignoring a duplicate." % key)
            return
        self.seen.add(key)
        
        output_file = output_template % self.current_record['_volume']
        if not output_file in self.outputs:
            self.outputs[output_file] = open(output_file, "w")
        out = self.outputs[output_file]
        outp = self.current_record.jsonable
        json.dump(outp, out)
        out.write("\n")
        self.object_stack = []
        self.current_record = None
        self.count += 1
        if not self.count % 10000:
            print(self.count)
        
Parser().parse(open(input_file))
