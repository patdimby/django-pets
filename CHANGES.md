# Maintenance changes

- Added documentation, repository metadata, a focused UTF-8 dependency list, isolated test settings and CI.
- Corrected template/static paths, optional mail defaults, production database configuration and development-only toolbar registration.
- Removed an obsolete distutils import and an unused Summernote app registration.
- Replaced import-time catalog queries and shared mutable context with per-request querysets.
- Made optional content/images safe, pagination forgiving and missing products return 404; corrected the checkout template.
- Gave unfinished subscription/contact handlers explicit 501 responses.
- Fixed cart session serialization, quantities, clear behavior, deleted products and coupon validity checks.
- Corrected optional cart/coupon imports and namespaces, removed a nonexistent recommender and added a cart template and coupon migration.
- Fixed invalid like input and forward/reverse like count signals; restored image auth navigation and login/logout templates.
- Added image download timeout/status checks and safe extension parsing, including query strings.
- Retained unfinished business workflows and documented their boundaries.
