#!/bin/bash
img1=$1; img2=$2
echo "Layers: $img1 $(docker image inspect "$img1" --format '{{len .RootFS.Layers}}') vs $img2 $(docker image inspect "$img2" --format '{{len .RootFS.Layers}}')"
shared=$(comm -12 <(docker image inspect "$img1" --format '{{range .RootFS.Layers}}{{.}}{{println}}{{end}}' | sort) <(docker image inspect "$img2" --format '{{range .RootFS.Layers}}{{.}}{{println}}{{end}}' | sort) | wc -l)
echo "Shared layers: $shared (cache hit potential: $((shared*100/${LAYERS1:-1}))%)"
diff <(docker history "$img1" --format "{{.CreatedBy}}" | head -n 10) <(docker history "$img2" --format "{{.CreatedBy}}" | head -n 10)
