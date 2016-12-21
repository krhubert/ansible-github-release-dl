#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: github_release_dl
short_description: Download GitHub Releases
description:
    - Download Github Releases
version_added: 2.2
options:
    token:
        required: true
        description:
            - Github Personal Access Token for authenticating
    user:
        required: true
        description:
            - The GitHub account that owns the repository
    repo:
        required: true
        description:
            - Repository name
    version:
        required: true
        description:
            - Version to download or 'latest'

    asset_name:
        required: false 
        description:
            - Asset name to download (if not specify then tarball will be downloaded)

    dest:
        required: true
        description:
            - Path for save release

author:
    - "Hubert Krauze (krhubert@gmail.com)"
requirements:
    - "github3.py >= 1.0.0a4"
'''

EXAMPLES = '''
- name: download latest release main binary file of test/test
  github_release_dl:
    token: tokenabc1234567890
    user: testuser
    repo: testrepo
    asset_name: main
    version: latest
    dest: /tmp/main
'''

try:
    import github3

    HAS_GITHUB_API = True
except ImportError:
    HAS_GITHUB_API = False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            repo=dict(required=True),
            user=dict(required=True),
            token=dict(required=True, no_log=True),
            asset_name=dict(required=False),
            version=dict(required=True),
            dest=dict(required=True),
        ),
        supports_check_mode=True
    )

    if not HAS_GITHUB_API:
        module.fail_json(msg='Missing requried github3 module (check docs or install with: pip install github3)')

    repo = module.params['repo']
    user = module.params['user']
    token = module.params['token']
    asset_name = module.params['asset_name']
    version = module.params['version']
    dest = module.params['dest']

    # login to github
    try:
        gh = github3.login(token=str(token))
        # test if we're actually logged in
        gh.me()
    except github3.AuthenticationFailed:
        e = get_exception()
        module.fail_json(msg='Failed to connect to Github: %s' % e)

    repository = gh.repository(str(user), str(repo))

    if not repository:
        module.fail_json(msg="Repository %s/%s doesn't exist" % (user, repo))

    if version == 'latest':
        release = repository.latest_release()
    else:
        release = repository.release_from_tag(str(version))

    if not release:
        module.fail_json(msg="Repository %s/%s doesn't have release %s" % (user, repo, version))

    # find asset id to download
    if asset_name:
        for asset in release.assets():
            if asset.name == asset_name:
                asset_id = asset.id
                break
        asset = release.asset(asset_id)
        asset.download(str(dest))
    else:
        release.archive('tarball', str(dest))

    module.exit_json()

from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
