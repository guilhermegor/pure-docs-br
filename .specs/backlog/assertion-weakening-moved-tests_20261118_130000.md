# Assertion-weakening: moved tests

- [x] fix/66-assertion-weakening-moved-tests judge a test that moved to another test file against its merge-base version instead of reporting it deleted
- [x] fix/66-assertion-weakening-moved-tests also clear moved tests when git reports the split source as a deleted file (D plus A rows, no rename)
