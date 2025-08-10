from glob import glob
from typing import Iterable
from xml.etree.ElementTree import Element, ElementTree
from dataclasses import dataclass


def find_annotation_files(root: str) -> list[str]:
    return glob(f"{root}/**/*.stxsm", recursive=True)


@dataclass
class AnnotationFile:
    tree: ElementTree

    @classmethod
    def from_stxsm_file(cls, path: str):
        tree = ElementTree()
        tree.parse(path)
        return cls(tree)

    @property
    def file_id(self) -> str:
        return self.tree.getroot().attrib["ID"]

    @property
    def samplerate(self) -> int:
        return int(self.tree.getroot().attrib["SR"])

    @property
    def segments(self) -> list["Segment"]:
        """A list of all annotated segments without the final 'Signal.All' one"""
        segments = self.tree.findall("ASeg")
        segments = filter(lambda x: x.attrib["ID"] != "Signal.All", segments)
        return list(segments)


@dataclass
class Segment:
    element: Element

    @property
    def id(self) -> str:
        return self.element.attrib["ID"]

    @property
    def start(self) -> int:
        return int(self.element.attrib["P"])

    @start.setter
    def start(self, value: int):
        self.attributes["P"] = str(value)

    @property
    def length(self) -> int:
        return int(self.element.attrib["L"])

    @property
    def attributes(self) -> dict[str, str]:
        return self.element.attrib


class CheetaAnnotationFile(AnnotationFile):
    @property
    def segments(self) -> list["CheetaSegment"]:
        return list(map(CheetaSegment, super().segments))

    def get_segment(self, vocnr: int) -> "CheetaSegment":
        return next((x for x in self.segments if x.vocnr == vocnr))

    @property
    def vocalisations(self) -> Iterable["CheetaSegment"]:
        return filter(CheetaSegment.is_vocalisation, self.segments)


class CheetaSegment(Segment):
    def is_single_voc(self) -> bool:
        return self.attributes["class"] == "single_voc"

    def is_vocalisation(self) -> bool:
        return "vocnr" in self.attributes.keys()

    @property
    def stimulus_id(self) -> int:
        return int(self.attributes["stimulus"])

    @property
    def vocnr(self) -> int:
        return int(self.attributes.get("vocnr", "-1"))

    @property
    def distance(self) -> int:
        return int(self.attributes["distance"])

    def __repr__(self) -> str:
        return f"CheetaSegment({self.attributes})"

    def __hash__(self) -> int:
        return hash(self.id)
