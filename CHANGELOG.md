# Change log for ITS Lost and Found

## 1.5.0 - 2019-01-08

### Added/Changed
- Add new ITS Manager permissions group to control access to Django admin page. Members of this group will have access to Change and Add Locations and Categories.
- Expose Categories in Django admin (see above).
- Add lost and found statistics widget to home page. This dashboard shows the number of items checked-in and returned by day, year, and current user.
- Add Datatables.js to AdminItemList (client-side sorting, etc)
- Refactor AdminItemList view and forms.
  - Remove redundant columns for clarity and design (all info on detail page).
  - Add year filter and current status (last action) filter.
  - Initialize filter to current year and "Checked-in" status in order to improve performance of common use case.
- Add odin autocomplete field on AdminActionForm

### Fixed
- Fix failing tests. Skip unnecessary and/or fragile tests and update Travis CI configuration Continuous integration/testing server).

### Maintenance
- Update all Python dependencies
- Update LDAP server hostname


## 1.4.0 - 2018-01-03
- Update Django to 1.11
- Modernize for newer arctasks and arcutils versions
- Use WDT ldap group (instead of ARC) when applying developer staff access

## 1.3.0 - 2016-12-20


## 1.2.0 - 2016-06-21

### Changed

- Made links to item status logs less prominent in item list to save
  space and so they don't stand out too much.

### Fixed

- Fixed location and category filtering of items. These were broken
  because the form sends PKs, but the filter function was trying to do
  lookups by name.
- Made Item status-related properties more robust. We now make sure an
  Item has statuses before attempting to access its first or last status
  or attributes of those statuses.


## 1.1.0 - 2016-06-20

### Added

- Added an item status log page for non-admin users. This page was
  previously only available to admins and always included the admin
  actions form.

## Changed

- Changed the email text for possible owner notifications to be more
  informative including using the location's long name.



## 1.0.0 - 2016-05-02

Tagging this release as 1.0.0 is somewhat arbitrary. Previous versions
weren't tagged. Compared to earlier versions, this version has been
cleaned up, converted into a distutils package, and made deployable with
ARCTasks.

## Pre-1.0

???
