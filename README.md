# LLM Learning Lab

[![CI](https://github.com/tianhao67/llm-learning/actions/workflows/ci.yml/badge.svg)](https://github.com/tianhao67/llm-learning/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)

涓€涓潰鍚戝垵瀛﹁€呯殑 **LLM 搴旂敤瀹炶返**椤圭洰锛氱敤 OpenAI 鍏煎鎺ュ彛璋冪敤澶фā鍨嬶紝缁冧範甯歌鎻愮ず璇嶆ā寮忥紝
骞剁敤 Streamlit 瀹炵幇涓€涓€屽涔犻渶姹傞棶鍗?鈫?涓€у寲瀛︿範寤鸿銆嶇殑灏忓簲鐢ㄣ€?
> 璇存槑锛氭湰椤圭洰鏄涔犲ぇ妯″瀷鍩虹璇剧▼鏃剁殑缁冧範鏁寸悊锛岄噸鐐逛笉鏄畻娉曞垱鏂帮紝鑰屾槸鎶婇浂鏁ｈ剼鏈?> 鏁寸悊鎴?*缁撴瀯娓呮櫚銆佸彲娴嬭瘯銆佸彲澶嶇幇**鐨勫皬宸ョ▼銆傞槄璇讳唬鐮佹椂璇蜂互瀛︿範鍙傝€冧负涓伙紝瀹冧笉杩芥眰
> 鐢熶骇鍙敤銆?
---

## 鍔熻兘

- **缁熶竴鐨勬ā鍨嬪鎴风**锛氬悓涓€浠戒唬鐮侀€氳繃 `OPENAI_BASE_URL` / `OPENAI_MODEL` 鍦?  DeepSeek銆侀€氫箟鍗冮棶銆丱penAI銆丱llama 涔嬮棿鍒囨崲銆?- **浜旂鎻愮ず璇嶆ā寮?*锛氭枃鏈垎绫汇€佸皯鏍锋湰绀轰緥銆佹€濈淮閾俱€佽鑹叉壆婕斻€丣SON 缁撴瀯鍖栬緭鍑恒€?- **缁撴瀯鍖栬緭鍑鸿В鏋?*锛氳嚜鍔ㄥ墺绂?` ```json ` 浠ｇ爜鍧楀苟鍋氭湰鍦版牎楠岋紝涓嶄俊浠绘ā鍨嬪師濮嬭緭鍑恒€?- **Streamlit 闂嵎搴旂敤**锛氬～鍐?6 涓棶棰橈紝鐢熸垚涓€у寲瀛︿範寤鸿锛屽彲鏌ョ湅瀹屾暣 Prompt銆?- **鍛戒护琛屽伐鍏?*锛歚python -m llm_demo "浣犵殑闂"`锛屾敮鎸?`--json`銆乣--system` 绛夊弬鏁般€?- **娴嬭瘯涓?CI**锛氱绾垮崟鍏冩祴璇?+ GitHub Actions锛坮uff + pytest锛孭ython 3.10 / 3.12锛夈€?- **瀵嗛挜瀹夊叏**锛歚.env` 宸插拷鐣ワ紝浠撳簱鍙繚鐣?`.env.example`锛屾棩蹇椾笌鐣岄潰缁熶竴鎵撶爜銆?
## 鐩綍缁撴瀯

```text
.
鈹溾攢鈹€ app.py                     # Streamlit 闂嵎搴旂敤鍏ュ彛
鈹溾攢鈹€ llm_demo/
鈹?  鈹溾攢鈹€ __init__.py
鈹?  鈹溾攢鈹€ __main__.py            # 鍛戒护琛屽叆鍙ｏ紙python -m llm_demo锛?鈹?  鈹溾攢鈹€ client.py              # OpenAI 鍏煎瀹㈡埛绔皝瑁咃紙chat / chat_json锛?鈹?  鈹溾攢鈹€ config.py              # 璇诲彇 .env锛屾牎楠岄厤缃紝瀵嗛挜鎵撶爜
鈹?  鈹溾攢鈹€ prompts.py             # 闂嵎鎻愮ず璇?+ 浜旂鎻愮ず璇嶆ā寮?鈹?  鈹斺攢鈹€ utils.py               # 浠庢ā鍨嬭緭鍑轰腑鎻愬彇 JSON
鈹溾攢鈹€ examples/
鈹?  鈹溾攢鈹€ 01_hello_llm.py        # 鏈€灏忚皟鐢?鈹?  鈹溾攢鈹€ 02_prompt_patterns.py  # 浜旂妯″紡瀵规瘮
鈹?  鈹斺攢鈹€ 03_json_output.py      # 缁撴瀯鍖栬緭鍑轰笌鏍￠獙
鈹溾攢鈹€ tests/                     # pytest 鍗曞厓娴嬭瘯锛堜笉鑱旂綉銆佷笉闇€瑕佺湡瀹?Key锛?鈹溾攢鈹€ docs/notes.md              # 瀛︿範绗旇锛氭帴鍙ｅ師鐞嗐€佹彁绀鸿瘝鎶€宸с€佹姤閿欐帓鏌?鈹溾攢鈹€ .github/workflows/ci.yml   # GitHub Actions
鈹溾攢鈹€ .env.example               # 鐜鍙橀噺妯℃澘
鈹溾攢鈹€ pyproject.toml             # 渚濊禆銆乺uff銆乸ytest 閰嶇疆
鈹斺攢鈹€ LICENSE
```

## 蹇€熷紑濮?
鐜瑕佹眰锛歅ython 3.10+锛屽彲璁块棶鎵€閫夋ā鍨嬪钩鍙扮殑缃戠粶銆?
```bash
# 1. 鍏嬮殕椤圭洰
git clone https://github.com/tianhao67/llm-learning.git
cd llm-learning

# 2. 鍒涘缓铏氭嫙鐜锛圵indows PowerShell锛?python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS / Linux
# python -m venv .venv && source .venv/bin/activate

# 3. 瀹夎锛?e 琛ㄧず浠ュ彲缂栬緫妯″紡瀹夎鏈寘锛?pip install -e ".[dev]"

# 4. 閰嶇疆瀵嗛挜锛氬鍒舵ā鏉垮苟濉叆鑷繁鐨勫€?copy .env.example .env        # macOS / Linux: cp .env.example .env

# 5. 璺戠涓€涓ず渚?python examples/01_hello_llm.py
```

### 杩愯绀轰緥

```bash
python examples/01_hello_llm.py                     # 鏈€灏忚皟鐢?python examples/02_prompt_patterns.py               # 渚濇璺戜簲绉嶆彁绀鸿瘝妯″紡
python examples/02_prompt_patterns.py -p json_output --text "鎴戝彨灏忔槑锛屽湪鍗椾含璇讳功锛屼細 Python"
python examples/03_json_output.py -o output/movies.json
```

### 杩愯 Web 搴旂敤

```bash
streamlit run app.py
```

娴忚鍣ㄦ墦寮€缁堢鎻愮ず鐨勫湴鍧€锛堥粯璁?<http://localhost:8501>锛夛紝濉啓闂嵎鍚庣偣鍑汇€岀敓鎴愬涔犲缓璁€嶏紝
渚ц竟鏍忓彲浠ヨ皟鏁?`temperature`銆佹煡鐪嬪綋鍓嶆ā鍨嬩笌鎵撶爜鍚庣殑 Key銆?
### 鍛戒护琛屽伐鍏?
```bash
python -m llm_demo "鐢ㄤ竴鍙ヨ瘽瑙ｉ噴浠€涔堟槸 RAG"
python -m llm_demo "鎶婁笅闈㈣繖鍙ヨ瘽缈昏瘧鎴愯嫳鏂囷細浠婂ぉ澶╂皵寰堝ソ"
python -m llm_demo --system "浣犳槸涓€涓弗璋ㄧ殑鎶€鏈瘎瀹? "杩欐浠ｇ爜鏈変粈涔堥棶棰橈細print(eval(input()))"
python -m llm_demo --json "鐢?JSON 杩斿洖锛歿'name': '灏忔槑', 'city': '鍗椾含'}"
```

## 閰嶇疆椤?
| 鍙橀噺 | 蹇呭～ | 榛樿鍊?| 璇存槑 |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | 鏄?| 鏃?| 骞冲彴绛惧彂鐨?API Key |
| `OPENAI_BASE_URL` | 鍚?| `https://api.deepseek.com` | OpenAI 鍏煎鎺ュ彛鍦板潃 |
| `OPENAI_MODEL` | 鍚?| `deepseek-chat` | 妯″瀷鍚嶇О |

淇敼 `.env` 鍚庨渶瑕侀噸鏂拌繍琛岀▼搴忥紙Streamlit 闇€閲嶅惎锛夈€?
## 鏀寔鐨勫钩鍙?
| 骞冲彴 | `OPENAI_BASE_URL` | `OPENAI_MODEL` 绀轰緥 |
| --- | --- | --- |
| DeepSeek | `https://api.deepseek.com` | `deepseek-chat` |
| 闃块噷浜戠櫨鐐硷紙閫氫箟鍗冮棶锛?| `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-turbo` / `qwen-plus` |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` |
| 鏈湴 Ollama | `http://localhost:11434/v1` | `qwen2.5:7b` |

> 鏈湴 Ollama 鐨?Key 鍙互闅忎究濉紝浣嗘湇鍔￠渶瑕佸厛 `ollama serve` 鍚姩銆?
## 杩欎釜椤圭洰缁冨埌浜嗕粈涔?
| 浣嶇疆 | 娑夊強鐨勭煡璇嗙偣 |
| --- | --- |
| `llm_demo/config.py` | 鐜鍙橀噺绠＄悊銆侀厤缃牎楠屻€佹晱鎰熶俊鎭墦鐮併€乨ataclass |
| `llm_demo/client.py` | OpenAI 鍏煎鎺ュ彛銆佹秷鎭鑹诧紙system/user锛夈€佸弬鏁颁紶閫?|
| `llm_demo/prompts.py` | 鎻愮ず璇嶇粨鏋勶細鎸囦护 + 灏戞牱鏈?+ 杈撳叆 + 绾︽潫 |
| `llm_demo/utils.py` | 妯″瀷杈撳嚭鐨勪笉纭畾鎬у鐞嗐€丣SON 鎻愬彇涓庢牎楠?|
| `app.py` | Streamlit 琛ㄥ崟銆乣st.session_state`銆乣st.cache_resource`銆侀敊璇彁绀?|
| `tests/` | pytest銆乵onkeypatch銆佺敤鍋囧璞℃浛韬殧绂荤綉缁滆皟鐢?|
| `.github/workflows/ci.yml` | GitHub Actions 鐭╅樀鏋勫缓銆佷緷璧栫紦瀛樸€乴int + test |

## 寮€鍙?
```bash
pip install -e ".[dev]"

pytest -q          # 杩愯娴嬭瘯锛堜笉闇€瑕?API Key锛屼笉浼氳仈缃戯級
ruff check .       # 浠ｇ爜妫€鏌?ruff format .      # 浠ｇ爜鏍煎紡鍖?```

娴嬭瘯鍏ㄩ儴绂荤嚎锛氶厤缃鍙栫敤 `monkeypatch` 娉ㄥ叆鐜鍙橀噺锛屽鎴风鐢ㄥ亣鐨?`chat.completions`
鏇胯韩锛屼笉浼氫骇鐢熶换浣?API 璋冪敤璐圭敤銆?
## 瀹夊叏璇存槑

- 浠撳簱涓?*涓嶅寘鍚换浣曠湡瀹炲瘑閽?*锛宍.env` 涓?`.streamlit/secrets.toml` 鍧囪 `.gitignore` 蹇界暐銆?- 绋嬪簭鎵撳嵃閰嶇疆鏃剁粺涓€浣跨敤 `mask_key()` 鎵撶爜銆?- 濡傛灉璇彁浜や簡 Key锛岃绔嬪埢鍒板钩鍙版帶鍒跺彴鍚婇攢骞堕噸鏂扮敓鎴愶紝鍚屾椂娓呯悊 Git 鍘嗗彶
  锛坄git filter-repo` 鎴?GitHub 鐨?secret scanning 鎻愮ず锛夈€?
## Roadmap

- [x] 缁熶竴瀹㈡埛绔笌閰嶇疆绠＄悊
- [x] 浜旂鎻愮ず璇嶆ā寮忕ず渚?- [x] Streamlit 闂嵎搴旂敤
- [x] 鍗曞厓娴嬭瘯涓?CI
- [ ] 澧炲姞澶氳疆瀵硅瘽锛堜繚鐣欎笂涓嬫枃锛夌ず渚?- [ ] 澧炲姞 RAG 灏忕ず渚嬶細鐢ㄨ绋嬭祫鏂欏仛妫€绱㈤棶绛?- [ ] 澧炲姞鎻愮ず璇嶇増鏈姣斾笌浜哄伐璇勫垎琛紙璇勬祴鎰忚瘑锛?- [ ] 閮ㄧ讲鍒?Streamlit Community Cloud锛屽苟鍦?README 闄勪笂鍦ㄧ嚎鍦板潃
- [ ] 鏀寔娴佸紡杈撳嚭锛坄stream=True`锛夛紝鏀瑰杽浜や簰浣撻獙

## 宸茬煡灞€闄?
- 鍙仛鍗曡疆瀵硅瘽锛屾病鏈夎蹇嗗拰涓婁笅鏂囩鐞嗭紱
- 鎻愮ず璇嶄负鍥哄畾妯℃澘锛屾病鏈夊仛 A/B 瀵规瘮涓庨噺鍖栬瘎娴嬶紱
- 鏈鐞嗗苟鍙戙€侀噸璇曚笌璇锋眰闄愭祦锛屼笉閫傚悎鐩存帴鐢ㄤ簬鐢熶骇锛?- 搴旂敤鏈仛鐢ㄦ埛杈撳叆瀹℃牳锛屼粎浣滀负瀛︿範婕旂ず銆?
## 璁稿彲璇?
鏈」鐩熀浜?[MIT License](LICENSE) 寮€婧愶紝娆㈣繋鍙傝€冧笌淇敼銆?