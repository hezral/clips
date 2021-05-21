desktop_file = i18n.merge_file(
  input: 'com.github.hezral.clips.desktop.in',
  output: 'com.github.hezral.clips.desktop',
  type: 'desktop',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'applications')
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils,
    args: [desktop_file]
  )
endif

appstream_file = i18n.merge_file(
  input: 'com.github.hezral.clips.appdata.xml.in',
  output: 'com.github.hezral.clips.appdata.xml',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'appdata')
)

appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
  test('Validate appstream file', appstream_util,
    args: ['validate', appstream_file]
  )
endif

install_data('com.github.hezral.clips.gschema.xml',
  install_dir: join_paths(get_option('datadir'), 'glib-2.0/schemas')
)

compile_schemas = find_program('glib-compile-schemas', required: false)
if compile_schemas.found()
  test('Validate schema file', compile_schemas,
    args: ['--strict', '--dry-run', meson.current_source_dir()]
  )
endif

icon_sizes = ['16', '24', '32', '48', '64', '128']
foreach i : icon_sizes
    install_data(
        join_paths('icons', i, meson.project_name() + '.svg'),
        install_dir: join_paths(get_option ('datadir'), 'icons', 'hicolor', i + 'x' + i, 'apps')
    )
    install_data(
        join_paths('icons', i, meson.project_name() + '.svg'),
        install_dir: join_paths(get_option ('datadir'), 'icons', 'hicolor', i + 'x' + i + '@2', 'apps')
    )
endforeach

install_data(
    join_paths('icons', '128', meson.project_name() + '.svg'),
    install_dir: join_paths(get_option ('datadir'), 'icons', 'hicolor', 'scalable', 'apps'),
    rename: meson.project_name() + '.svg'
)

pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())

install_data('application.css',
  install_dir: join_paths(pkgdatadir, 'clips', 'data')
)

other_icon_sources = [
  join_paths('icons', meson.project_name() + '-' + 'coffee' + '.svg'),
  join_paths('icons', meson.project_name() + '-' + 'enabled-symbolic' + '.svg'),
  join_paths('icons', meson.project_name() + '-' + 'flowbox-symbolic' + '.svg'),
  join_paths('icons', meson.project_name() + '-' + 'hidepswd-symbolic' + '.svg'),
  join_paths('icons', meson.project_name() + '-' + 'info-symbolic' + '.svg'),
  join_paths('icons', meson.project_name() + '-' + 'protect-symbolic' + '.svg'),
  join_paths('icons', meson.project_name() + '-' + 'revealpswd-symbolic' + '.svg'),
  join_paths('icons', meson.project_name() + '-' + 'select-symbolic' + '.svg'),
  join_paths('icons', meson.project_name() + '-' + 'select' + '.svg'),
  join_paths('icons', meson.project_name() + '-' + 'settings-symbolic' + '.svg'),
  join_paths('icons', meson.project_name() + '-' + 'view-symbolic' + '.svg'),
  join_paths('icons', meson.project_name() + '-' + 'unprotect-symbolic' + '.svg'),
  join_paths('icons', 'edit-copy-symbolic' + '.svg'),
  join_paths('icons', 'edit-delete-symbolic' + '.svg'),
  join_paths('icons', 'quick-search' + '.svg'),
]
iconsdir = join_paths(pkgdatadir, 'clips', 'data', 'icons')
install_data(other_icon_sources, install_dir: iconsdir)

image_sources = [
  join_paths('images', 'help_clip_actions_dark' + '.png'),
  join_paths('images', 'help_clip_actions_light' + '.png'),
  join_paths('images', 'help_clip_info_dark' + '.png'),
  join_paths('images', 'help_clip_info_light' + '.png'),
  join_paths('images', 'help_clipsapp_toggle_dark' + '.png'),
  join_paths('images', 'help_clipsapp_toggle_light' + '.png'),
  join_paths('images', 'help_column_number_dark' + '.png'),
  join_paths('images', 'help_column_number_light' + '.png'),
  join_paths('images', 'help_doubleclick_copy_dark' + '.png'),
  join_paths('images', 'help_doubleclick_copy_light' + '.png'),
  join_paths('images', 'help_hide_clips_dark' + '.png'),
  join_paths('images', 'help_hide_clips_light' + '.png'),
  join_paths('images', 'help_multiselect_dark' + '.png'),
  join_paths('images', 'help_multiselect_light' + '.png'),
  join_paths('images', 'help_quick_copy_dark' + '.png'),
  join_paths('images', 'help_quick_copy_light' + '.png'),
  join_paths('images', 'help_run_clips_dark' + '.png'),
  join_paths('images', 'help_run_clips_light' + '.png'),
  join_paths('images', 'help_search_dark' + '.png'),
  join_paths('images', 'help_search_light' + '.png'),
  join_paths('images', 'help_settings_dark' + '.png'),
  join_paths('images', 'help_settings_light' + '.png'),
  join_paths('images', 'help_switch_views_dark' + '.png'),
  join_paths('images', 'help_switch_views_light' + '.png'),
]
imagesdir = join_paths(pkgdatadir, 'clips', 'data', 'images')
install_data(image_sources, install_dir: imagesdir)