# -*- coding: utf-8 -*-

import os
import re

import pytest
from click.testing import CliRunner

import git_app_version.version
from git_app_version.__main__ import dump as git_app_version_main
from test_helpers import git_utils


@pytest.fixture()
def tmpdir(tmpdir_factory):
    cwd = os.getcwd()
    new_cwd = tmpdir_factory.mktemp('empty')
    new_cwd_path = str(new_cwd)
    os.chdir(new_cwd_path)
    yield new_cwd_path
    os.chdir(cwd)


@pytest.fixture()
def git_repo(tmpdir_factory):
    cwd = os.getcwd()
    new_cwd = tmpdir_factory.mktemp('git_repo')
    new_cwd_path = str(new_cwd)
    os.chdir(new_cwd_path)
    repo = git_utils.init(repo_dir=new_cwd_path)
    git_utils.commit(repo, message='commit 1',)
    git_utils.tag(repo, version='0.1.2',)
    yield repo
    os.chdir(cwd)


def test_version():
    runner = CliRunner()

    arg = ['--version']
    expected = 'git-app-version ' + git_app_version.version.__version__ + "\n"

    result = runner.invoke(git_app_version_main, arg)
    assert result.exit_code == 0
    assert result.output == expected


def test_not_git_repository(tmpdir):
    runner = CliRunner()

    arg = [tmpdir]
    expected = ("Error Writing version config file :"
                " The directory '{}' is not a git repository.\n")

    result = runner.invoke(git_app_version_main, arg)
    assert result.exit_code == 1
    assert result.output == expected.format(tmpdir)


def test_quiet(git_repo):
    runner = CliRunner()

    arg = ['-q', git_repo.working_tree_dir]
    output_path = os.path.join(git_repo.working_tree_dir, 'version.json')

    result = runner.invoke(git_app_version_main, arg)

    assert result.exit_code == 0
    assert os.path.exists(output_path)


def test_json(git_repo):
    runner = CliRunner()

    arg = [git_repo.working_tree_dir]
    output_path = os.path.join(git_repo.working_tree_dir, 'version.json')

    result = runner.invoke(git_app_version_main, arg)

    assert result.output.find('Git commit :') != -1
    assert re.search(r"version\s+0.1.2", result.output)
    assert result.output.find('written to :') != -1
    assert result.output.find(output_path) != -1

    assert os.path.exists(output_path)
    assert result.exit_code == 0
