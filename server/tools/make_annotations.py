# -*- coding: utf-8 -*-
import os
import re
import json
from enum import Enum


class ProtoType(Enum):
    Message = 0
    Enum = 1


def listdirs(path, depth=0, res=None):
    '''
    遍历文件夹，path 要遍历的路径. depth 文件夹层级, 0 表示当前层
    '''
    if res == None:
        res = list()

    if depth < 0:
        return res

    files = os.listdir(path)
    for filename in files:
        filepath = os.path.join(path, filename)
        if os.path.isdir(filepath):
            listdirs(filepath, depth - 1, res)
        else:
            res.append(os.path.normpath(filepath))
    return res


proto_lua_map = dict()
proto_lua_map["int32"] = "integer"
proto_lua_map["int64"] = "integer"
proto_lua_map["uint32"] = "integer"
proto_lua_map["uint64"] = "integer"
proto_lua_map["sint32"] = "integer"
proto_lua_map["sint64"] = "integer"
proto_lua_map["fixed32"] = "integer"
proto_lua_map["fixed64"] = "integer"
proto_lua_map["sfixed32"] = "integer"
proto_lua_map["sfixed64"] = "integer"
proto_lua_map["bool"] = "boolean"
proto_lua_map["float"] = "number"
proto_lua_map["double"] = "number"
proto_lua_map["string"] = "string"
proto_lua_map["bytes"] = "string"


def to_lua_type(prototype):
    if prototype in proto_lua_map:
        return proto_lua_map[prototype]
    else:
        return prototype


def make_message(name, fields):
    res = ""
    res += "---@class %s\n" % (name)
    for line_tuple in fields:
        if line_tuple[0] is not None:
            if line_tuple[0].startswith("repeated"):
                if line_tuple[4] is not None:
                    res += "---@field public %s %s[] @%s\n" % (
                        line_tuple[2], to_lua_type(line_tuple[1]), line_tuple[4].strip('\n \t/'))
                else:
                    res += "---@field public %s %s[]\n" % (
                        line_tuple[2], to_lua_type(line_tuple[1]))
            elif line_tuple[0] == "map":
                if line_tuple[5] is not None:
                    res += "---@field public %s table<%s, %s> @%s\n" % (line_tuple[3], to_lua_type(
                        line_tuple[1]), to_lua_type(line_tuple[2]), line_tuple[5].strip('\n \t/'))
                else:
                    res += "---@field public %s table<%s, %s>\n" % (
                        line_tuple[3], to_lua_type(line_tuple[1]), to_lua_type(line_tuple[2]))
            else:
                print("wrong key", line_tuple[0])
        else:
            if line_tuple[4] is not None:
                res += "---@field public %s %s @%s\n" % (
                    line_tuple[2], to_lua_type(line_tuple[1]), line_tuple[4].strip('\n \t/'))
            else:
                res += "---@field public %s %s\n" % (
                    line_tuple[2], to_lua_type(line_tuple[1]))
    # res += "M.%s = {}\n\n" % (name)
    res += "\n\n"
    return res


def make_enum(name, fields):
    res = ""
    res += "---@class %s\n" % (name)
    res += "local %s = {\n" % (name)
    for line_tuple in fields:
        if line_tuple[0] is not None:
            if len(line_tuple) == 3:
                if line_tuple[2] is not None:
                    res += "    %s = %s, -- %s\n" % (
                        line_tuple[0], line_tuple[1], line_tuple[2].strip('\n \t/'))
                else:
                    res += "    %s = %s,\n" % (line_tuple[0], line_tuple[1])
            else:
                print("wrong enum", line_tuple)
    res += "}"
    return res


class EmmyLuaIntelliSense:
    def __init__(self):
        pass

    def parse_proto(self, protopath):
        '''解析proto文件'''

        message_name_re = re.compile(r'message\s+(\w+)')
        enum_name_re = re.compile(r'enum\s+(\w+)')

        message_field_re = re.compile(
            r'\s*(repeated)?\s*(\w+)\s+(\w+)\s*=\s*(\d+)\s*;\s*(\/\/.*)?')
        message_map_field_re = re.compile(
            r'\s*(map)\s*<\s*(\w+)\s*,\s*(\w+)\s*>\s+(\w+)\s*=\s*(\d+);\s*(\/\/.*)?')
        enum_field_re = re.compile(r'\s*(\w+)\s*=\s*(\d+);\s*(\/\/.*)?')

        proto_list = list()

        protofiles = listdirs(protopath, 3)

        for filepath in protofiles:
            if not filepath.endswith(".proto"):
                continue
            parse_stack = list()

            with open(filepath, 'r', encoding='utf-8') as fobj:
                for line in fobj:
                    if line.lstrip().startswith("//"):
                        continue
                    nameres = message_name_re.search(line)
                    if nameres is not None:
                        parse_stack.append(
                            (ProtoType.Message, nameres.group(1), list()))
                    nameres = enum_name_re.search(line)
                    if nameres is not None:
                        parse_stack.append(
                            (ProtoType.Enum, nameres.group(1), list()))

                    if line.find("{") != -1 and line.find("//") == -1:
                        continue

                    if len(parse_stack) > 0:
                        last = parse_stack[(len(parse_stack)-1)]
                        if last[0] == ProtoType.Message:
                            tmp = message_map_field_re.search(line)
                            if tmp is not None:
                                line_group = tmp.groups()
                                last[2].append(line_group)
                            else:
                                tmp = message_field_re.search(line)
                                if tmp is not None:
                                    line_group = tmp.groups()
                                    last[2].append(line_group)
                                else:
                                    # print("1", line)
                                    pass
                        elif last[0] == ProtoType.Enum:
                            tmp = enum_field_re.search(line)
                            if tmp is not None:
                                line_group = tmp.groups()
                                last[2].append(line_group)
                            else:
                                # print("2", line)
                                pass
                        if line.find("}") != -1:
                            proto_list.append(parse_stack.pop())

        return proto_list

    def make_proto_annotations(self, proto_list, json_verify_out_file):
        message_content = ""
        enum_content = ""
        enum_name_list = list()

        jsonconcept = dict()

        for one in proto_list:
            protoType = one[0]
            name = one[1]
            fields = one[2]

            if protoType == ProtoType.Message:
                message = dict()
                for line_tuple in fields:
                    field = dict()
                    value_name = ""
                    if line_tuple[0] == "repeated":
                        field["container"] = "array"
                        field["value_type"] = line_tuple[1]
                        value_name = line_tuple[2]
                        field["value_index"] = line_tuple[3]
                        if line_tuple[4]:
                            field["comment"] = line_tuple[4].strip('\n \t/')
                    elif line_tuple[0] == "map":
                        field["container"] = "object"
                        field["key_type"] = line_tuple[1]
                        field["value_type"] = line_tuple[2]
                        value_name = line_tuple[3]
                        field["value_index"] = line_tuple[4]
                        if line_tuple[5]:
                            field["comment"] = line_tuple[5].strip('\n \t/')
                    else:
                        field["value_type"] = line_tuple[1]
                        value_name = line_tuple[2]
                        field["value_index"] = line_tuple[3]
                        if line_tuple[4]:
                            field["comment"] = line_tuple[4].strip('\n \t/')
                    message[value_name] = field
                jsonconcept[name] = message

            if protoType == ProtoType.Enum:
                enum_content += make_enum(name, fields)
                enum_content += "\n\n"
                enum_name_list.append(name)
            elif protoType == ProtoType.Message:
                message_content += make_message(name, fields)

        with open(json_verify_out_file, "w+", encoding='utf-8') as fobj:
            fobj.write(json.dumps(jsonconcept, ensure_ascii=False))

        enum_content += "\n\n"
        enum_content += "return {\n"
        for enum_name in enum_name_list:
            enum_content += "    %s=%s,\n" % (enum_name, enum_name)
        enum_content += "}\n"

        return message_content, enum_content

    def make_game_annotations(self, logicpath):
        logicsfiles = listdirs(logicpath, 2)
        logicannotations = dict()
        for filepath in logicsfiles:
            filepath = filepath.replace("\\", "/")
            tmp = filepath.split('/')
            servicename = tmp[len(tmp)-2]
            parentpath, filename = os.path.split(filepath)
            if os.path.samefile(logicpath, parentpath):
                continue
            shotname, extension = os.path.splitext(filename)
            if not servicename in logicannotations:
                logicannotations[servicename] = list()
            logicannotations[servicename].append(shotname)

        content = "\n\n"
        for (k, v) in dict.items(logicannotations):
            content += "\n\n"
            content += "---@class %s_scripts\n" % (k)
            for one in v:
                content += "---@field %s %s\n" % (one, one)
        return content

    def make_conf_annotations(self, confpath):
        conffiles = listdirs(confpath)
        conf_list = list()
        for filepath in conffiles:
            parentpath, filename = os.path.split(filepath)
            shotname, extension = os.path.splitext(filename)
            conf_list.append(shotname)

        content = "\n\n"
        content += "---@class static_conf\n"
        for confname in conf_list:
            if confname == "constant_func":
                content += "---@field %s %s\n" % (confname, confname)
            else:
                content += "---@field %s %s_cfg[]\n" % (confname, confname)
        return content

    def run(self, proto_src_dir, game_dir, game_config_dir, json_verify_out_file):

        protolist = self.parse_proto(proto_src_dir)

        message_content, enum_content = self.make_proto_annotations(
            protolist, json_verify_out_file)

        with open("Annotations.lua", 'w+', encoding='utf-8') as fobj:
            fobj.write(message_content)

        with open("ProtoEnum.lua", 'w+', encoding='utf-8') as fobj:
            fobj.write(enum_content)

        logic_content = self.make_game_annotations(game_dir)

        conf_content = self.make_conf_annotations(game_config_dir)

        with open("Annotations.lua", 'a', encoding='utf-8') as fobj:
            fobj.write(logic_content)
            fobj.write(conf_content)

        return protolist


intelliSense = EmmyLuaIntelliSense()

protolist = intelliSense.run(
    proto_src_dir="../protocol/",
    game_dir="../game/",
    game_config_dir="../static/table/",
    json_verify_out_file="../protocol/json_verify.json"
)
# you can use protolist do something
