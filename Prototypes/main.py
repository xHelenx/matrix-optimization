from os import write
from  readWriteFile import read_file, write_action_file, write_reward_file

#read_file("example_xml.xml")
write_action_file("test.xml","1", "M1", "M2")
write_reward_file("reward.xml")
print("done")
