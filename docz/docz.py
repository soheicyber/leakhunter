"""Inserts a tracking bug into docx files"""

import shutil

from os import makedirs, getcwd

from typing import Optional

TEMP_FOLDER = "docz_tmp"
OUTPUT_FILENAME = "output.docx"

REL = '<Relationship TargetMode="External" ' + \
    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"' + \
    ' Id="rId1337" Target='

DRAWING = """<w:drawing mc:Ignorable="w14 wp14">
	<wp:inline distT="0" distB="0" distL="0" distR="0">
		<wp:extent cx="1" cy="1"/>
		<wp:effectExtent l="0" t="0" r="0" b="0"/>
		<wp:docPr id="4" name="pengwings"/>
		<wp:cNvGraphicFramePr>
			<a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/>
		</wp:cNvGraphicFramePr>
		<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
			<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
				<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
					<pic:nvPicPr>
						<pic:cNvPr id="0" name="cumberbatch"/>
						<pic:cNvPicPr/>
					</pic:nvPicPr>
					<pic:blipFill>
						<a:blip r:link="rId1337"/>
						<a:stretch>
							<a:fillRect/>
						</a:stretch>
					</pic:blipFill>
					<pic:spPr>
						<a:xfrm>
							<a:off x="0" y="0"/>
							<a:ext cx="1" cy="1"/>
						</a:xfrm>
						<a:prstGeom prst="rect">
							<a:avLst/>
						</a:prstGeom>
					</pic:spPr>
				</pic:pic>
			</a:graphicData>
		</a:graphic>
	</wp:inline>
</w:drawing>"""


class Docz():
    """Embeds a webbug in a docx file."""

    def __init__(self, filename, url, target, agent):
        # The name of the file template to embed the bug in.
        self.filename = filename
        self.url = url  # The url to the listening server
        self.target = target  # The target identifier
        self.agent = agent  # The agent identifier
        self.connstring = "%s?agent=%s&target=%s" % (url, agent, target)
        self.processing_complete = False

    def _get_rel(self) -> str:
        """return the injection value using the connstring."""
        return REL + '"' + self.connstring.replace("&", "&#38;") + '" />'

    def _unzip(self):
        self.processing_complete = False
        """Unzip the docx file into an archive on disk."""
        makedirs(TEMP_FOLDER)
        shutil.unpack_archive("{file}".format(file=self.filename), TEMP_FOLDER)

    def _inject(self):
        """Inject the bug into the docx file."""
        document_data = ""
        with open("{tmp}/word/document.xml".format(tmp=TEMP_FOLDER), "r") as document:
            document_data = document.read()

        temp = document_data.split("</w:body>")
        temp.append("</w:body>" + temp[1])
        temp[1] = DRAWING

        document_data = "".join(temp)

        with open("{tmp}/word/document.xml".format(tmp=TEMP_FOLDER), "w") as document:
            document.write(document_data)

        with open("{tmp}/word/_rels/document.xml.rels".format(tmp=TEMP_FOLDER), "r") as rels:
            rels_data = rels.read()

        temp = rels_data.split("</Relationships>")
        temp.append(self._get_rel())
        temp.append("</Relationships>")

        rels_data = "".join(temp)

        with open("{tmp}/word/_rels/document.xml.rels".format(tmp=TEMP_FOLDER), "w") as rels:
            rels.write(rels_data)

    def _zip(self):
        """Zip the open archive into docx."""
        shutil.make_archive(
            "output.docx", "{cwd}/{tmp}".format(cwd=getcwd(), tmp=TEMP_FOLDER))

        shutil.move("{tmp}/output.docx".format(tmp=TEMP_FOLDER),
                    "./{output}".format(output=OUTPUT_FILENAME))
        shutil.rmtree(TEMP_FOLDER)
        self.processing_complete = True

    def run(self):
        """Run the process to unzip, inject, and zip."""
        self._unzip()
        self._inject()
        self._zip()

    def get_file_location(self) -> Optional[str]:
        """Return the location of the output file."""
        if self.processing_complete:
            return "{cwd}/{out}".format(cwd=getcwd, out=OUTPUT_FILENAME)
        return None
