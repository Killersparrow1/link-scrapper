#!/bin/bash
#
# scrape_thread.sh - Extract and categorize links from forum threads
#
# Usage: ./scrape_thread.sh <thread_url> [output_dir] [browser]
#
# Examples:
#   ./scrape_thread.sh "https://forums.socialmediagirls.com/threads/xxx.123456"
#   ./scrape_thread.sh "https://forums.socialmediagirls.com/threads/xxx.123456" /path/to/output firefox
#   ./scrape_thread.sh "https://forums.socialmediagirls.com/threads/xxx.123456" /path/to/output chrome
#
# Requirements:
#   - gallery-dl (with browser cookie support)
#   - Firefox/Chrome/Chromium/Brave with logged-in session
#

set -euo pipefail

THREAD_URL="${1:-}"
OUT_DIR="${2:-./output}"
BROWSER="${3:-firefox}"

# Known image hosting domains
IMG_DOMAINS=(
    "imagepond.net/i/"
    "goonbox.cr/img/"
    "imagebam.com/view/"
    "simp6.cuckcapital.cr/images"
    "cosplayrule34.com/images"
    "media.imagepond.net/media/images"
    "catbox.moe"
    "imgbox.com"
    "postimg.cc"
    "ibb.co"
    "files.catbox.moe"
    "jpghub.nl"
    "pbs.twimg.com"
    "preview.redd.it"
    "static.*hentai-cosplays.com"
    "s[0-9]+.dpic.me"
    "img.kiwi"
    "i.postimg.cc"
    "i.imgur.com"
    "pixhost.to"
    "imgur.com"
)

# Known video hosting domains/patterns
VID_DOMAINS=(
    "imagepond.net/videos/"
    "turbo.cr/embed/"
    "pornmz.com/video"
    "eporner.com/video"
    "beeg.com/"
    "bunkr.cr/a/"
    "bunkr.si/f/"
    "bunkr.pk/f/"
    "bunkr.media/f/"
    "bunkr.ac/v/"
    "bunkr.ax/v/"
    "bunkr.black/v/"
    "bunkr.cat/v/"
    "bunkr.fi/f/"
    "bunkr.ph/a/"
    "bunkr.red/f/"
    "bunkrrr.org/v/"
    "bunkrrr.org/a/"
    "bunkrrr.org/f/"
    "bunkr.si/a/"
    "bunkr.site/a/"
    "bunkr.site/f/"
    "bunkr.si/v/"
    "bunkr.sk/a/"
    "bunkr.sk/v/"
    "filester.me/f/"
    "filester.si/d/"
    "gofile.io/d/"
    "pixeldrain.com/l/"
    "pixeldrain.com/u/"
    "saint2.cr/embed/"
    "saint2.su/embed/"
    "turbo.cr/v/"
    "fileditchfiles.me"
    "stream.bunkr."
    "erome.com/a/"
    "cyberdrop.me/f/"
    "cyberfile.me/"
    "mega.nz/file/"
    "coomer.party/"
    "thothub.ch/videos/"
    "pornforce.com/"
    "pornolab.net/"
    "xvideos.com/video"
    "pornhub.com/view_video"
    "redgifs.com/users/"
    "onlyfans.com/"
    "manyvids.com/Video/"
)

IMG_EXTS="(jpg|jpeg|png|gif|webp|bmp|svg)"
VID_EXTS="(mp4|webm|mkv|avi|mov|flv|m4v|mpeg|mpg|ogv)"

usage() {
    cat <<EOF
Usage: $0 <thread_url> [output_dir] [browser]

Arguments:
  thread_url    URL of the forum thread to scrape
  output_dir    Directory to save output files (default: ./output)
  browser       Browser to extract cookies from: firefox, chrome, chromium, brave (default: firefox)

Output files:
  all_urls.txt      - All unique URLs found
  image_urls.txt    - Image URLs
  video_urls.txt    - Video URLs
  other_urls.txt    - Uncategorized URLs
  summary.txt       - Summary statistics

Examples:
  $0 "https://forums.socialmediagirls.com/threads/xxx.123456"
  $0 "https://forums.socialmediagirls.com/threads/xxx.123456" /my/output chrome
EOF
    exit 1
}

log() {
    echo "[$(date '+%H:%M:%S')] $*"
}

check_deps() {
    local missing=()
    command -v gallery-dl >/dev/null || missing+=("gallery-dl")
    command -v sort >/dev/null || missing+=("sort")
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        log "ERROR: Missing dependencies: ${missing[*]}"
        log "Install gallery-dl: pip install gallery-dl"
        exit 1
    fi
}

validate_browser() {
    case "$BROWSER" in
        firefox|chrome|chromium|brave) ;;
        *)
            log "ERROR: Unsupported browser '$BROWSER'. Use: firefox, chrome, chromium, brave"
            exit 1
            ;;
    esac
}

build_regex() {
    local -n domains=$1
    local regex=""
    for domain in "${domains[@]}"; do
        if [[ -n "$regex" ]]; then
            regex+="|"
        fi
        regex+="$domain"
    done
    echo "$regex"
}

main() {
    [[ -z "$THREAD_URL" ]] && usage
    
    check_deps
    validate_browser
    
    mkdir -p "$OUT_DIR"
    
    log "Starting scrape of: $THREAD_URL"
    log "Output directory: $OUT_DIR"
    log "Browser: $BROWSER"
    
    local all_urls="$OUT_DIR/all_urls.txt"
    local img_urls="$OUT_DIR/image_urls.txt"
    local vid_urls="$OUT_DIR/video_urls.txt"
    local other_urls="$OUT_DIR/other_urls.txt"
    local summary="$OUT_DIR/summary.txt"
    
    # Step 1: Fetch all URLs using gallery-dl
    log "Fetching URLs with gallery-dl..."
    gallery-dl --cookies-from-browser "$BROWSER" --get-urls "$THREAD_URL" 2>/dev/null \
        | grep -v "^\[.*\]" \
        | sort -u > "$all_urls"
    
    local total=$(wc -l < "$all_urls")
    log "Found $total unique URLs"
    
    if [[ $total -eq 0 ]]; then
        log "WARNING: No URLs found. Check cookies/login status."
        exit 1
    fi
    
    # Step 2: Build classification regexes
    local img_domain_regex=$(build_regex IMG_DOMAINS)
    local vid_domain_regex=$(build_regex VID_DOMAINS)
    
    # Step 3: Classify URLs
    log "Classifying URLs..."
    > "$img_urls"
    > "$vid_urls"
    > "$other_urls"
    
    while IFS= read -r url; do
        [[ -z "$url" ]] && continue
        
        local classified=0
        
        # Check image extensions
        if [[ "$url" =~ \.$IMG_EXTS(\?|$) ]]; then
            echo "$url" >> "$img_urls"
            classified=1
        # Check image domains
        elif [[ "$url" =~ $img_domain_regex ]]; then
            echo "$url" >> "$img_urls"
            classified=1
        # Check video extensions
        elif [[ "$url" =~ \.$VID_EXTS(\?|$) ]]; then
            echo "$url" >> "$vid_urls"
            classified=1
        # Check video domains
        elif [[ "$url" =~ $vid_domain_regex ]]; then
            echo "$url" >> "$vid_urls"
            classified=1
        else
            echo "$url" >> "$other_urls"
            classified=1
        fi
    done < "$all_urls"
    
    # Step 4: Generate summary
    local img_count=$(wc -l < "$img_urls")
    local vid_count=$(wc -l < "$vid_urls")
    local other_count=$(wc -l < "$other_urls")
    
    cat > "$summary" <<EOF
Scrape Summary
==============
Thread: $THREAD_URL
Date: $(date)
Browser: $BROWSER

Total URLs: $total
  Images: $img_count
  Videos: $vid_count
  Other:  $other_count

Output files:
  $all_urls
  $img_urls
  $vid_urls
  $other_urls
  $summary
EOF
    
    log "Done!"
    cat "$summary"
}

main "$@"