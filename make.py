from makegen import *

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
            auto_mkdir(["{0} {1} $(SOFLAGS) -o $@ {2}{3}".format(
                compiler,
                flags,
                " ".join(
                    make_escape(shell_quote(obj_fn))
                    for obj_fn in obj_fns
                ),
                extra_libs,
            )], out_fn=out_filename),
        )},
        macros=merge_dicts(DEFAULT_MACROS[language], macros),
    ).merge(*(obj for obj in objs
              if not obj.hint.get("invisible_rule", False)),
            hint_merger=do_nothing)

wclock_config_h = simple_command(
    "sed -e '3s|/\\*\\(.*\\)\\*/|\\1|' >$@ <{0}",
    "include/wclock_config.h", ["src/wclock_config.h"])

i_wclock = simple_command(
    "sed -e '3s|/\\*\\(.*\\)\\*/|\\1|' >$@ <{0}",
    "include/wclock.h", ["src/wclock.h", wclock_config_h])

l_wclock = build_library("lib/wclock", [
    compile_source("src/wclock.c",
                   extra_flags=
                   "-include include/wclock_config.h "
                   "$(wclock_cflags)",
                   extra_deps=[wclock_config_h]),
], extra_libs="$(wclock_libs)")

testprogram = build_program("bin/wclock_test", [
    compile_source("src/test.c", extra_flags="-Iinclude"),
], libraries=[Library("wclock")], extra_flags="-Llib", extra_deps=[
    i_wclock,
    l_wclock,
])

check = simple_command(
    "LD_LIBRARY_PATH=lib DYLD_LIBRARY_PATH=lib {0}", "check",
    [testprogram], phony=True)

alias("all", [
    i_wclock,
    l_wclock,
]).merge(
    check,
).save("Makefile.in")
