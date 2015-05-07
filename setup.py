from setuptools import setup, find_packages

setup(
    name="django_granular_permissions",
	version="0.3",
	description="Django Granular Permissions allow you to setup per-row permissions.",
    author="Yazzg",
	author_email="yazzg...@gmail.com",
	maintainer="Rob Yates",
	maintainer_email="",
	url="https://github.com/ryates/django-granular-permissions-redux",
	packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)

