import argparse
import json
import logging
import os
from pathlib import Path

from .models import ChannelType, OutputFormat
from .pipeline import PIFPipeline
from .release import ReleaseManager


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=level,
    )


def handle_check(args: argparse.Namespace) -> None:
    manager = ReleaseManager(token=args.token)
    results = manager.check_upstream_updates(state_dir=Path(args.state_dir))

    has_updates = len(results) > 0
    payload = {"new_release": has_updates, "results": results}

    if github_output := os.getenv("GITHUB_OUTPUT"):
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"new_release={'true' if has_updates else 'false'}\n")
            f.write(f"results={json.dumps(results)}\n")

    print(json.dumps(payload, indent=2))


def handle_build(args: argparse.Namespace) -> None:
    pipeline = PIFPipeline(
        channel=ChannelType(args.channel),
        format_type=OutputFormat(args.format),
        output_dir=Path(args.output_dir),
    )

    if args.file:
        content = Path(args.file).read_text(encoding="utf-8")
        profile = pipeline.process_prop_content(content)
        out_path = Path(args.output_dir) / f"{Path(args.file).stem}.json"
        out_path.write_text(profile.model_dump_json(indent=2), encoding="utf-8")
        print(f"Generated: {out_path}")
        return

    if args.assets_json:
        assets = json.loads(args.assets_json)
        generated_paths = []
        for item in assets:
            try:
                dest = pipeline.process_zip_url(item["name"], item["url"])
                generated_paths.append(str(dest))
            except Exception as exc:
                logging.error("Failed processing %s: %s", item.get("name"), exc)

        if args.manifest:
            Path(args.manifest).write_text("\n".join(generated_paths), encoding="utf-8")

        print(f"Generated {len(generated_paths)} files.")


def handle_publish(args: argparse.Namespace) -> None:
    manager = ReleaseManager(token=args.token)
    files = [
        Path(line.strip())
        for line in Path(args.manifest).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    manager.publish_release(
        target_repo=args.repo,
        files=files,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="pif-config-generator",
        description="Automated Play Integrity profile extraction and release tool",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose debug logging")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Check
    p_check = subparsers.add_parser("check", help="Check upstream repositories for new releases")
    p_check.add_argument("--token", default=None, help="GitHub API token")
    p_check.add_argument("--state-dir", default="state", help="Directory storing release tag trackers")
    p_check.set_defaults(func=handle_check)

    # Build
    p_build = subparsers.add_parser("build", help="Extract and build PIF JSON profiles")
    p_build.add_argument("--channel", choices=["stable", "beta"], default="stable")
    p_build.add_argument("--format", choices=["extended", "legacy"], default="extended")
    p_build.add_argument("--output-dir", default=".", help="Output directory for generated JSONs")
    p_build.add_argument("--file", help="Path to a single system.prop file")
    p_build.add_argument("--assets-json", help="JSON array of asset items with name and url")
    p_build.add_argument("--manifest", default="generated_files.txt", help="Output file list manifest")
    p_build.set_defaults(func=handle_build)

    # Publish
    p_pub = subparsers.add_parser("publish", help="Publish generated profiles to a GitHub release")
    p_pub.add_argument("--token", default=None, help="GitHub API token")
    p_pub.add_argument("--repo", required=True, help="Target GitHub repository (owner/repo)")
    p_pub.add_argument("--manifest", default="generated_files.txt", help="Manifest containing file paths")
    p_pub.set_defaults(func=handle_publish)

    args = parser.parse_args()
    setup_logging(args.verbose)
    args.func(args)


if __name__ == "__main__":
    main()
