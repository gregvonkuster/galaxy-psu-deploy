import yaml
import argparse
from collections import defaultdict

from bioblend import toolshed

DEFAULT_TOOL_SHED_URL = 'https://toolshed.g2.bx.psu.edu/'


class ToolSheds(defaultdict):
    default_factory = toolshed.ToolShedInstance

    def __missing__(self, key):
        print('Creating new ToolShedInstance for URL: %s\n', key)
        return self.default_factory(url=key)


tool_sheds = ToolSheds()


def update_file(fn, owner=None, name=None, without=False):
    with open(fn, 'r') as handle:
        tool_section_yml = yaml.safe_load(handle)

    # Update all tool_section_yml tools.
    for tool in tool_section_yml['tools']:
        # tool: {'name': 'prokka',
        #        'owner': 'crs4',
        #        'revisions': ['8a22554cdde2'],
        #        'tool_panel_section_label': 'Annotation',
        #        'tool_shed_url': 'https://toolshed.g2.bx.psu.edu/'}
        print("\n\ntool: %s" % str(tool))
        # If without, then if it is lacking, we should exec.
        print("Examining {owner}/{name}".format(**tool))

        if without:
            if 'revisions' in tool and not len(tool.get('revisions', [])) == 0:
                continue

        if not without and owner and tool['owner'] not in owner:
            continue

        if not without and name and tool['name'] != name:
            continue

        ts_url = tool.get('tool_shed_url', DEFAULT_TOOL_SHED_URL)
        if ts_url != DEFAULT_TOOL_SHED_URL:
            print('Non-default Tool Shed URL for %s/%s: %s', tool['owner'], tool['name'], ts_url)
        ts = tool_sheds[ts_url]

        print("Fetching updates for {owner}/{name}".format(**tool))

        try:
            revs = ts.repositories.get_ordered_installable_revisions(tool['name'], tool['owner'])
        except Exception as e:
            print(e)
            continue

        print('TS revisions: %s' % ','.join(revs))
        latest_rev = revs[-1]
        if latest_rev in tool.get('revisions', []):
            # The rev is already known, don't add again.
            continue

        print("Found newer revision of {owner}/{name} ({rev})".format(rev=latest_rev, **tool))

        # Get latest rev, if not already added, add it.
        if 'revisions' not in tool:
            tool['revisions'] = []

        if latest_rev not in tool['revisions']:
            # TS doesn't support utf8 and we don't want to either.
            tool['revisions'].append(str(latest_rev))

    with open(fn, 'w') as handle:
        yaml.dump(tool_section_yml, handle, default_flow_style=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('fn', type=argparse.FileType('r'), help="Tool.yaml file")
    parser.add_argument('--owner', action='append', help="Repository owner to filter on, anything matching this will be updated. Can be specified multiple times")
    parser.add_argument('--name', help="Repository name to filter on, anything matching this will be updated")
    parser.add_argument('--without', action='store_true', help="If supplied will ignore any owner/name and just automatically add the latest hash for anything lacking one.")
    parser.add_argument('--log', choices=('critical', 'error', 'warning', 'info', 'debug'), default='info')
    args = parser.parse_args()

    update_file(args.fn.name, owner=args.owner, name=args.name, without=args.without)
