import json
import pathlib
import pytest

from transpose import Transpose, TransposeConfig, TransposeEntry
from transpose.exceptions import TransposeError

from .utils import (
    ENTRY_NAME,
    ENTRY_STORE_PATH,
    STORE_PATH,
    TARGET_PATH,
    TRANSPOSE_CONFIG_PATH,
    setup_restore,
    setup_store,
    setup_apply,
)


@setup_store()
def test_init():
    t = Transpose(config_path=TRANSPOSE_CONFIG_PATH)
    assert t.config.entries.get(ENTRY_NAME)
    assert t.config_path == TRANSPOSE_CONFIG_PATH
    assert t.store_path == TRANSPOSE_CONFIG_PATH.parent


@setup_apply()
def test_apply():
    t = Transpose(config_path=TRANSPOSE_CONFIG_PATH)

    # Success
    t.apply(ENTRY_NAME)
    assert TARGET_PATH.is_symlink()
    assert ENTRY_STORE_PATH.is_dir()

    with pytest.raises(TransposeError, match="Entry does not exist"):
        t.apply("BadName")

    # Will remove the symlink created above and reapply
    # TODO: Check symlink path
    t.apply(ENTRY_NAME)
    assert TARGET_PATH.is_symlink()
    assert ENTRY_STORE_PATH.is_dir()

    # Target already exists, force not set
    TARGET_PATH.unlink()
    TARGET_PATH.mkdir()
    with pytest.raises(TransposeError, match="Entry path already exists"):
        t.apply(ENTRY_NAME)

    # Target already exists, force set (Create backup of original path)
    t.apply(ENTRY_NAME, force=True)
    backup_path = TARGET_PATH.with_suffix(".backup")

    assert backup_path.is_dir()
    assert TARGET_PATH.is_symlink()
    assert ENTRY_STORE_PATH.is_dir()


@setup_restore()
def test_restore():
    t = Transpose(config_path=TRANSPOSE_CONFIG_PATH)

    # Success
    t.restore(ENTRY_NAME)
    assert TARGET_PATH.is_dir()
    assert not TARGET_PATH.is_symlink()
    assert not ENTRY_STORE_PATH.exists()

    with pytest.raises(TransposeError, match="Could not locate entry by name"):
        t.restore("BadName")


@setup_restore()
def test_restore_path_conflicts():
    t = Transpose(config_path=TRANSPOSE_CONFIG_PATH)

    # Target already exists, force not set
    TARGET_PATH.mkdir()
    with pytest.raises(TransposeError, match="Entry path already exists"):
        t.restore(ENTRY_NAME)

    t.restore(ENTRY_NAME, force=True)
    backup_path = TARGET_PATH.with_suffix(".backup")

    assert backup_path.is_dir()
    assert TARGET_PATH.is_dir()
    assert not TARGET_PATH.is_symlink()
    assert not ENTRY_STORE_PATH.exists()
    assert not t.config.entries.get(ENTRY_NAME)


@setup_store()
def test_store():
    t = Transpose(config_path=TRANSPOSE_CONFIG_PATH)

    # Success
    t.store("TestEntry", TARGET_PATH)
    assert TARGET_PATH.is_symlink()
    assert STORE_PATH.joinpath("TestEntry").is_dir()
    assert t.config.entries["TestEntry"].path == str(TARGET_PATH)


@setup_store()
def test_store_conflicts():
    t = Transpose(config_path=TRANSPOSE_CONFIG_PATH)

    with pytest.raises(TransposeError, match="Entry already exists"):
        t.store(ENTRY_NAME, TARGET_PATH)

    with pytest.raises(TransposeError, match="Source path does not exist"):
        t.store("TestEntry", "UnknownPath/")

    STORE_PATH.joinpath("TestEntry").mkdir()
    with pytest.raises(TransposeError, match="Store path already exists"):
        t.store("TestEntry", TARGET_PATH)
    STORE_PATH.joinpath("TestEntry").rmdir()


@setup_store()
def test_config_add():
    pass  # TODO


@setup_store()
def test_config_get():
    pass  # TODO


@setup_store()
def test_config_list():
    pass  # TODO


@setup_store()
def test_config_remove():
    pass  # TODO


@setup_store()
def test_config_save():
    pass  # TODO


@setup_store()
def test_config_load():
    pass  # TODO
