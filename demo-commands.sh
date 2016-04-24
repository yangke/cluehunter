#!/bin/bash
#CVE-2008-1686
python cluehunter.py -ps '*' -vs mode -l 1 -t test/gdb_logs/speex/CVE-2008-1686/speex-1.1.12/speexdec/gdb-speex-1.1.12_speexdec_mode.txt -n gdb-speex-1.1.12_speexdec_mode

#python cluehunter.py -ps '*' -vs mode -t gdb.txt -n gdb-speex-1.1.12_speexdec_mode

#python cluehunter.py -ps 'N' -vs modeID -i 165 -t test/gdb_logs/speex/CVE-2008-1686/speex-1.1.12/speexdec/gdb-speex-1.1.12_speexdec_mode.txt -n gdb-speex-1.1.12_speexdec_modeID

#python cluehunter.py -ps 'N' -vs modeID -i 165 -t gdb.txt -n gdb-speex-1.1.12_speexdec_modeID

#swfmill
#python cluehunter.py -ps 'N' -vs length -t /home/yangke/workspace/cluehunter/test/gdb_logs/swfmill-0.3.3/gdb-swfmill-0.3.3_length.txt -n gdb-swfmill-0.3.3_length

#swftools
#python cluehunter.py -ps '*' -vs 't->data' -t gdb.txt -n gdb-swftools-0.9.2_swfdump_t-data_i

