from makegen import *

def build_archive(out_filename, objs):
    import os
    objs = tuple(objs)
    obj_fns = [obj.default_target for obj in objs]
    language, libs, macros = get_linker_flags(objs, [])
    compiler, flags = get_clike_language_info(language)
    out_dir = os.path.dirname(out_filename)
    if out_dir:
        out_dir += "/"
    out_bn = os.path.basename(out_filename)
    return Ruleset(
        rules={"{0}$(LIBPRE){1}$(AREXT)".format(out_dir, out_bn): (
            frozenset(obj_fns),
            auto_mkdir(["$(AR) $(ARFLAGS) $@" + (
                "".join(
                    " " + make_escape(shell_quote(obj_fn))
                    for obj_fn in obj_fns
                )
            ), "$(RANLIB) $@"], out_fn=out_filename),
        )},
        macros=merge_dicts(DEFAULT_MACROS[language], macros),
    ).merge(*(obj for obj in objs
              if not obj.hint.get("invisible_rule", False)),
            hint_merger=do_nothing)

def build_library(out_filename, objs, extra_libs=""):
    import os
    objs = tuple(objs)
    obj_fns = [obj.default_target for obj in objs]
    language, libs, macros = get_linker_flags(objs, [])
    compiler, flags = get_clike_language_info(language)
    out_dir = os.path.dirname(out_filename)
    if out_dir:
        out_dir += "/"
    out_bn = os.path.basename(out_filename)
    if extra_libs:
        extra_libs = " " + extra_libs
    return Ruleset(
        rules={"{0}$(LIBPRE){1}$(SOEXT)".format(out_dir, out_bn): (
            frozenset(obj_fns),
            auto_mkdir(["{0} {1} $(SOFLAGS) -o $@{2}{3}".format(
                compiler,
                flags,
                "".join(
                    " " + make_escape(shell_quote(obj_fn))
                    for obj_fn in obj_fns
                ),
                extra_libs,
            )], out_fn=out_filename),
        )},
        macros=merge_dicts(DEFAULT_MACROS[language], macros),
    ).merge(*(obj for obj in objs
              if not obj.hint.get("invisible_rule", False)),
            hint_merger=do_nothing)

def install_files(deps, extra_deps=[], name="install"):
    import os
    deps = list(deps)
    dep_fns = sorted(dep.default_target for dep in deps)
    extra_dep_fns = [dep.default_target for dep in extra_deps]
    dirs = set()
    for dep_fn in dep_fns:
        dirs.add(os.path.dirname(dep_fn))
    commands = []
    for d in sorted(dirs):
        commands.append("install -d $(DESTDIR)$(PREFIX)/" + d)
    for dep_fn in dep_fns:
        mode = "644"
        if dep_fn.endswith("$(SOEXT)") or dep_fn.endswith("$(EXEEXT)"):
            mode = "755"
        commands.append("install -c -m{0} {1} $(DESTDIR)$(PREFIX)/{1}"
                        .format(mode, dep_fn))
    return Ruleset(
        rules={name: (frozenset(dep_fns + extra_dep_fns), commands)},
        phonys=[name],
    ).merge(*deps, hint_merger=do_nothing)

i_wclock_config = simple_command(
    "sed -e '3s|/\\*\\(.*\\)\\*/|\\1|' >$@ <{0}",
    "include/wclock_config.h", ["src/wclock_config.h"])

i_wclock = simple_command(
    "sed -e '3s|/\\*\\(.*\\)\\*/|\\1|' >$@ <{0}",
    "include/wclock.h", ["src/wclock.h", i_wclock_config])

srcs = [
    compile_source("src/wclock.c",
                   extra_flags=
                   "-include include/wclock_config.h "
                   "$(wclock_cflags)",
                   extra_deps=[i_wclock_config]),
]

lar_wclock = build_archive("lib/wclock", srcs)

lso_wclock = build_library("lib/wclock", srcs, extra_libs="$(wclock_libs)")

testprogram = build_program("bin/wclock_test", [
    compile_source("src/test.c", extra_flags="-Iinclude"),
], libraries=[Library("wclock")], extra_flags="-Llib", extra_deps=[
    i_wclock,
    lar_wclock,
])

all_rule = alias("all", [
    i_wclock,
    lar_wclock,
    lso_wclock,
])

check = simple_command([
    "LD_LIBRARY_PATH=lib:$$LD_LIBRARY_PATH "
    "DYLD_LIBRARY_PATH=lib:$$DYLD_LIBRARY_PATH "
    "PATH=lib:$$PATH "
    "{0}"
], "check", [testprogram], phony=True)

install = install_files([
    i_wclock,
    i_wclock_config,
    lar_wclock,
    lso_wclock,
])

all_rule.merge(
    check,
    install,
).save("Makefile.in")
