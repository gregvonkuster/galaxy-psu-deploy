Scripts for maintaining the Galaxy PSU instance.

The update_tools.py script accepts a tool section .yml file with all revisions sections
removed, retrieves the latest revision for each tool from the Tool Shed, and re-added the
revisions section with the retrieved latest revision.  This provides a simple way to
update the tools in a tool section to the latest revision of each tool.  The script
accepts other parameter inputs (e.g., repository / owner, etc) that support other
scenarios for updating tools, but using the --without parameter is the most used scenario.

example command:
python update_tools.py --without ../tools/phenotype_association.yml
