BATCH_SIZE=500

cd "$1"

for file in pdf/*.pdf; do
    name=$(basename "$file" .pdf)
    pages=$(pdfinfo "$file" | grep "Pages:" | awk '{print $2}')
    if (( pages > BATCH_SIZE ))
    then
        typeset -i i
        batches=$(( pages / BATCH_SIZE ))
        for ((i=0; i<batches; i++)); do
            printf '%s\0%s\0%s\0' "$1/$file" $(( i*BATCH_SIZE + 1 ))-$(( (i+1)*BATCH_SIZE )) "$1/pretreated/${name}_$(printf "%03d" $i).csv"
        done
        printf '%s\0%s\0%s\0' "$1/$file" $(( batches * BATCH_SIZE + 1 ))-$pages "$1/pretreated/${name}_$(printf "%03d" $batches).csv"
    else
        printf '%s\0%s\0%s\0' "$1/$file" all "$1/pretreated/${name}.csv"
    fi
done
