#!/usr/bin/env python

""" Inserts tracking information into docx files """

import argparse
import sys
import os
import subprocess

REL = '<Relationship TargetMode="External" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Id="rId1337" Target='

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


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
      description='A script for embedding webbugs in docx files')
  parser.add_argument(
      '-f', '--file', help="The name of the file template to embed the bug in.", required=True)
  parser.add_argument(
      '-u', '--url', help='The url to the remote server', required=True)
  parser.add_argument(
      '-t', '--target', help='The target identifier', required=True)
  parser.add_argument(
      '-a', '--agent', help='The agent identifier', required=True)

  args = parser.parse_args()

  connstring = "%s?agent=%s&target=%s" % (args.url, args.agent, args.target)

  addrel = connstring.replace("&", "&#38;")
  rel = REL + '"' + addrel + '" />'

  subprocess.call(["mkdir", "docz_tmp"])
  subprocess.call(["unzip", "{file}".format(file=args.file), "-d", "docz_tmp")

  document= open("docz_tmp/word/document.xml", "r")
  document_data= document.read()
  document.close()

  temp= document_data.split("</w:body>")
  temp.append("</w:body>" + temp[1])
  temp[1]= DRAWING

  document_data= "".join(temp)

  document= open("docz_tmp/word/document.xml", "w")
  document.write(document_data)
  document.close()

  rels= open("docz_tmp/word/_rels/document.xml.rels", "r")
  rels_data= rels.read()
  rels.close()

  temp= rels_data.split("</Relationships>")
  temp.append(rel)
  temp.append("</Relationships>")

  rels_data= "".join(temp)

  rels= open("docz_tmp/word/_rels/document.xml.rels", "w")
  rels.write(rels_data)
  rels.close()

  cwd1= os.getcwd()
  cwd1= cwd1 + "/docz_tmp"

  p= subprocess.Popen("zip -r output.docx *",
                       stdout=None, shell=True, cwd=cwd1)
  p.wait()

  os.system(
      "mv docz_tmp/output.docx ./")
  os.system("rm -rf docz_tmp")
