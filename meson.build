project('com.github.hezral.clips',  
          version: '1.1.0',
    meson_version: '>= 0.49.0',
  default_options: [ 'warning_level=2',
                   ],
)

i18n = import('i18n')


subdir('data')
subdir('src')
subdir('po')

meson.add_install_script('build-aux/meson/postinstall.py')
