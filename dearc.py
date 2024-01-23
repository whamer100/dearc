from readma import Readma
import cli
import os
import gzip
from attrs import define


@define
class ArcHeader:
    unk0: int  # u32
    unk1: int  # u32
    entryCount: int  # u32
    entryTableOffset: int  # u32


@define
class ArcEntry:
    ident: bytes  # 4 byte identifier
    entrySize: int  # u32
    fileSize: int  # u32
    fileOffset: int  # u32
    fileName: str  # null terminated string


def readma_string(r: Readma) -> str:
    buf = ""
    while 1:
        c = r.read(1)
        if c == 0:
            return buf
        buf += chr(c)


class Dearc:
    def __init__(self, opt: cli.Options):
        self.opt = opt

    def run(self):
        root_inpath = os.path.abspath(self.opt.input)
        root_outpath = os.path.abspath(self.opt.output)
        for base, _, files in os.walk(root_inpath):
            # print("------")
            for fname in files:
                rel_path = os.path.relpath(base, root_inpath)
                source_path = os.path.join(root_inpath, rel_path)
                target_path = os.path.join(root_outpath, rel_path)
                rel_fname = os.path.join(rel_path, fname)
                source_fname = os.path.join(root_inpath, rel_fname)
                target_fname = os.path.join(root_outpath, rel_fname)
                # print(rel_path, rel_fname, source_fname, target_fname)
                # make skeleton
                os.makedirs(target_path, exist_ok=True)
                self.handle(source_fname, target_fname)

    @staticmethod
    def handle(fname: str, outpath: str):
        r = Readma(fname)
        magic = r.bytes(4)
        if magic == b"\x1F\x8B\x08\x08":  # gzip compressed
            r.seek(0)
            r = Readma(gzip.decompress(r.readall()))
            magic = r.bytes(4)
        if magic == b"DGKP":  # archive
            # we make a folder with the same name as the input file to avoid collisions
            os.makedirs(outpath, exist_ok=True)
            header = ArcHeader(
                r.read(4),  # unknown
                r.read(4),  # unknown
                r.read(4),  # entryCount
                r.read(4),  # entryTableOffset
            )
            # print(header)
            entries = []
            r.seek(header.entryTableOffset)
            for _ in range(header.entryCount):
                eIdent = r.bytes(4)
                eSize = r.read(4)
                e = Readma(r.bytes(eSize - 8))
                entries.append(ArcEntry(
                    eIdent,
                    eSize,
                    e.read(4),  # fileSize
                    e.read(4),  # fileOffset
                    readma_string(e)  # fileName
                ))
            # print(entries)
            for entry in entries:
                r.seek(entry.fileOffset)
                if entry.fileName == "":
                    entry.fileName = entry.ident.decode() + "_NONAME"
                outfname = os.path.join(outpath, entry.fileName)
                with open(outfname, 'wb') as fp:
                    fp.write(r.bytes(entry.fileSize))
        else:  # unidentified
            r.seek(0)
            with open(outpath, 'wb') as fp:
                fp.write(r.readall())  # just copy the existing file to the output, as we dont care what this is
