#!/usr/bin/env python3
"""Rebuild the local OAuth 2.0 RFC Markdown mirror.

The script downloads each RFC through mdzilla, converts it to Markdown, then
renames the exported `index.md` to the flat filename used by this directory.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


RFC_FILES = {
    2046: "rfc2046-multipurpose-internet-mail-extensions-mime-part-two-media-types.md",
    2119: "rfc2119-key-words-for-use-in-rfcs-to-indicate-requirement-levels.md",
    2246: "rfc2246-the-tls-protocol-version-1-0.md",
    2616: "rfc2616-hypertext-transfer-protocol-http-1-1.md",
    2617: "rfc2617-http-authentication-basic-and-digest-access-authentication.md",
    2818: "rfc2818-http-over-tls.md",
    3629: "rfc3629-utf-8-a-transformation-format-of-iso-10646.md",
    3986: "rfc3986-uniform-resource-identifier-uri-generic-syntax.md",
    4627: "rfc4627-the-application-json-media-type-for-javascript-object-notation-json.md",
    4647: "rfc4647-matching-of-language-tags.md",
    4949: "rfc4949-internet-security-glossary-version-2.md",
    5226: "rfc5226-guidelines-for-writing-an-iana-considerations-section-in-rfcs.md",
    5234: "rfc5234-augmented-bnf-for-syntax-specifications-abnf.md",
    5246: "rfc5246-the-transport-layer-security-tls-protocol-version-1-2.md",
    5280: "rfc5280-internet-x-509-public-key-infrastructure-certificate-and-certificate-revocation-list-crl-profile.md",
    5646: "rfc5646-tags-for-identifying-languages.md",
    6125: "rfc6125-service-identity-in-tls-with-x509-certificates.md",
    6265: "rfc6265-http-state-management-mechanism.md",
    6749: "rfc6749-the-oauth-2-0-authorization-framework.md",
    6750: "rfc6750-the-oauth-2-0-authorization-framework-bearer-token-usage.md",
    6838: "rfc6838-media-type-specifications-and-registration-procedures.md",
    7515: "rfc7515-json-web-signature-jws.md",
    7516: "rfc7516-json-web-encryption-jwe.md",
    7517: "rfc7517-json-web-key-jwk.md",
    7518: "rfc7518-json-web-algorithms-jwa.md",
    7519: "rfc7519-json-web-token-jwt.md",
    7591: "rfc7591-oauth-2-0-dynamic-client-registration-protocol.md",
    7643: "rfc7643-system-for-cross-domain-identity-management-core-schema.md",
    7662: "rfc7662-oauth-2-0-token-introspection.md",
    8126: "rfc8126-guidelines-for-writing-an-iana-considerations-section-in-rfcs.md",
    8174: "rfc8174-ambiguity-of-uppercase-vs-lowercase-in-rfc-2119-key-words.md",
    8259: "rfc8259-the-javascript-object-notation-json-data-interchange-format.md",
    8414: "rfc8414-oauth-2-0-authorization-server-metadata.md",
    8615: "rfc8615-well-known-uniform-resource-identifiers-uris.md",
    8628: "rfc8628-oauth-2-0-device-authorization-grant.md",
    8693: "rfc8693-oauth-2-0-token-exchange.md",
    8705: "rfc8705-oauth-2-0-mutual-tls-client-authentication-and-certificate-bound-access-tokens.md",
    8707: "rfc8707-resource-indicators-for-oauth-2-0.md",
    8725: "rfc8725-json-web-token-best-current-practices.md",
    8996: "rfc8996-deprecating-tls-1-0-and-tls-1-1.md",
    9068: "rfc9068-json-web-token-jwt-profile-for-oauth-2-0-access-tokens.md",
    9110: "rfc9110-http-semantics.md",
    9111: "rfc9111-http-caching.md",
    9325: "rfc9325-recommendations-for-secure-use-of-transport-layer-security-tls-and-datagram-transport-layer-security-dtls.md",
    9396: "rfc9396-oauth-2-0-rich-authorization-requests.md",
    9449: "rfc9449-oauth-2-0-demonstrating-proof-of-possession-dpop.md",
    9525: "rfc9525-service-identity-in-tls.md",
    9728: "rfc9728-oauth-2-0-protected-resource-metadata.md",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download, convert, and rename the OAuth 2.0 RFC mirror."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Directory that will receive the flat rfc*.md files.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove existing rfc*.md files in the output directory before writing.",
    )
    parser.add_argument(
        "--keep-export-dirs",
        action="store_true",
        help="Keep intermediate rfcXXXX export directories for inspection.",
    )
    return parser.parse_args()


def run_mdzilla(rfc: int, export_dir: Path) -> None:
    source = f"https://www.rfc-editor.org/rfc/rfc{rfc}.txt"
    subprocess.run(
        ["pnpx", "mdzilla", source, "--export", str(export_dir)],
        check=True,
    )


def validate_markdown(path: Path, rfc: int) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    if "Fetch Error" in text or "Failed to fetch" in text:
        raise RuntimeError(f"mdzilla wrote a fetch error for RFC {rfc}: {path}")
    if len(text.splitlines()) < 20:
        raise RuntimeError(f"export for RFC {rfc} looks too short: {path}")
    if f"Request for Comments: {rfc}" not in text[:2000] and f"RFC {rfc}" not in text[:2000]:
        raise RuntimeError(f"export for RFC {rfc} does not look like the expected RFC")


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="oauth2-rfc-mirror-") as tmp:
        tmp_dir = Path(tmp)
        built_files: list[Path] = []

        for rfc, filename in RFC_FILES.items():
            export_dir = tmp_dir / f"rfc{rfc}"
            print(f"Exporting RFC {rfc} -> {filename}", flush=True)
            run_mdzilla(rfc, export_dir)

            index = export_dir / "index.md"
            if not index.exists():
                raise RuntimeError(f"missing mdzilla export for RFC {rfc}: {index}")
            validate_markdown(index, rfc)

            built = tmp_dir / filename
            index.rename(built)
            built_files.append(built)

            if not args.keep_export_dirs:
                shutil.rmtree(export_dir)

        if args.clean:
            for existing in output_dir.glob("rfc*.md"):
                existing.unlink()

        for built in built_files:
            shutil.move(str(built), output_dir / built.name)

    generated = sorted(output_dir.glob("rfc*.md"))
    if len(generated) != len(RFC_FILES):
        raise RuntimeError(
            f"expected {len(RFC_FILES)} RFC files, found {len(generated)} in {output_dir}"
        )

    print(f"Generated {len(generated)} RFC Markdown files in {output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
