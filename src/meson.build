pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'clips')
gnome = import('gnome')

python = import('python')

conf = configuration_data()
# conf.set('PYTHON', python.find_installation('python3').path())
conf.set('PYTHON', '/usr/bin/python3')
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'clips.in',
  output: 'com.github.hezral.clips',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

clips_sources = [
  '__init__.py',
  'main.py',
  'main_window.py',
  'utils.py',
  'cache_manager.py',
  'clipboard_manager.py',
  'clips_supported.py',
  'clips_view.py',
  'custom_widgets.py',
  'info_view.py',
  'settings_view.py',
  'shake_listener.py',
  'active_window_manager.py',
  'filemanager_backend.py',
]
install_data(clips_sources, install_dir: moduledir)
