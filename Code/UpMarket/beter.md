

باگ های نهایی



1
عکس 1.png رو ببین خود پروژه بدون این که من دکمه تحلیل رو بزنم برا خودش یک لودینگ بی نهایت و بدون پردازش زده که من هم دکمه اش رو نزدن هم دیگه بلاک شده وافعا نمیئ تونم استفاده کنم !


2 
پخش کپشن هم طبق عکس 2.png هم مثله بخش قبل برای خودش یه لودینگ بی نهایت انداخته که من نزدم و خودش زده واین بخش هم بلاک کرده 


3
تحلیل رقبا 

ارور داد کلا

ggml_cuda_init: GGML_CUDA_FORCE_MMQ:    no
ggml_cuda_init: GGML_CUDA_FORCE_CUBLAS: no
ggml_cuda_init: found 1 CUDA devices:
  Device 0: NVIDIA GeForce RTX 3060, compute capability 8.6, VMM: yes, ID: GPU-31bc780f-6ab1-6151-aafe-6dc1e582c7d1
load_backend: loaded CUDA backend from C:\Users\Dragon\AppData\Local\Programs\Ollama\lib\ollama\cuda_v13\ggml-cuda.dll
time=2026-08-30T03:29:56.523+03:30 level=INFO source=ggml.go:104 msg=system CPU.0.SSE3=1 CPU.0.SSSE3=1 CPU.0.AVX=1 CPU.0.AVX_VNNI=1 CPU.0.AVX2=1 CPU.0.F16C=1 CPU.0.FMA=1 CPU.0.BMI2=1 CPU.0.LLAMAFILE=1 CPU.1.LLAMAFILE=1 CUDA.0.ARCHS=750,800,860,870,890,900,1000,1030,1100,1200,1210 CUDA.0.USE_GRAPHS=1 CUDA.0.PEER_MAX_BATCH_SIZE=128 compiler=cgo(clang)
time=2026-08-30T03:29:56.525+03:30 level=INFO source=runner.go:1001 msg="Server listening on 127.0.0.1:64491"
time=2026-08-30T03:29:56.533+03:30 level=INFO source=runner.go:895 msg=load request="{Operation:commit LoraPath:[] Parallel:1 BatchSize:512 FlashAttention:Enabled KvSize:8192 KvCacheType:q8_0 NumThreads:6 GPULayers:29[ID:GPU-31bc780f-6ab1-6151-aafe-6dc1e582c7d1 Layers:29(35..63)] MultiUserCache:false ProjectorPath: MainGPU:0 UseMmap:false}"
time=2026-08-30T03:29:56.534+03:30 level=INFO source=server.go:1350 msg="waiting for llama runner to start responding"
time=2026-08-30T03:29:56.534+03:30 level=INFO source=server.go:1384 msg="waiting for server to become available" status="llm server loading model"
ggml_backend_cuda_device_get_memory device GPU-31bc780f-6ab1-6151-aafe-6dc1e582c7d1 utilizing NVML memory reporting free: 11415830528 total: 12884901888
llama_model_load_from_file_impl: using device CUDA0 (NVIDIA GeForce RTX 3060) (0000:01:00.0) - 10886 MiB free
llama_model_loader: loaded meta data with 33 key-value pairs and 771 tensors from C:\Users\Dragon\.ollama\models\blobs\sha256-7ccc6415b2c7cb61ff8e01fec069d6f2fd6e213c509824d642c8a15c3d002e73 (version GGUF V3 (latest))
llama_model_loader: Dumping metadata keys/values. Note: KV overrides do not apply in this output.
llama_model_loader: - kv   0:                       general.architecture str              = qwen2
llama_model_loader: - kv   1:                               general.type str              = model
llama_model_loader: - kv   2:                               general.name str              = QwQ 32B
llama_model_loader: - kv   3:                           general.basename str              = QwQ
llama_model_loader: - kv   4:                         general.size_label str              = 32B
llama_model_loader: - kv   5:                            general.license str              = apache-2.0
llama_model_loader: - kv   6:                       general.license.link str              = https://huggingface.co/Qwen/QWQ-32B/b...
llama_model_loader: - kv   7:                   general.base_model.count u32              = 1
llama_model_loader: - kv   8:                  general.base_model.0.name str              = Qwen2.5 32B
llama_model_loader: - kv   9:          general.base_model.0.organization str              = Qwen
llama_model_loader: - kv  10:              general.base_model.0.repo_url str              = https://huggingface.co/Qwen/Qwen2.5-32B
llama_model_loader: - kv  11:                               general.tags arr[str,2]       = ["chat", "text-generation"]
llama_model_loader: - kv  12:                          general.languages arr[str,1]       = ["en"]
llama_model_loader: - kv  13:                          qwen2.block_count u32              = 64
llama_model_loader: - kv  14:                       qwen2.context_length u32              = 40960
llama_model_loader: - kv  15:                     qwen2.embedding_length u32              = 5120
llama_model_loader: - kv  16:                  qwen2.feed_forward_length u32              = 27648
llama_model_loader: - kv  17:                 qwen2.attention.head_count u32              = 40
llama_model_loader: - kv  18:              qwen2.attention.head_count_kv u32              = 8
llama_model_loader: - kv  19:                       qwen2.rope.freq_base f32              = 1000000.000000
llama_model_loader: - kv  20:     qwen2.attention.layer_norm_rms_epsilon f32              = 0.000010
llama_model_loader: - kv  21:                       tokenizer.ggml.model str              = gpt2
llama_model_loader: - kv  22:                         tokenizer.ggml.pre str              = qwen2
llama_model_loader: - kv  23:                      tokenizer.ggml.tokens arr[str,152064]  = ["!", "\"", "#", "$", "%", "&", "'", ...
llama_model_loader: - kv  24:                  tokenizer.ggml.token_type arr[i32,152064]  = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, ...
llama_model_loader: - kv  25:                      tokenizer.ggml.merges arr[str,151387]  = ["Ġ Ġ", "ĠĠ ĠĠ", "i n", "Ġ t",...
llama_model_loader: - kv  26:                tokenizer.ggml.eos_token_id u32              = 151645
llama_model_loader: - kv  27:            tokenizer.ggml.padding_token_id u32              = 151643
llama_model_loader: - kv  28:                tokenizer.ggml.bos_token_id u32              = 151643
llama_model_loader: - kv  29:               tokenizer.ggml.add_bos_token bool             = false
llama_model_loader: - kv  30:                    tokenizer.chat_template str              = {%- if tools %}\n    {{- '<|im_start|>...
llama_model_loader: - kv  31:               general.quantization_version u32              = 2
llama_model_loader: - kv  32:                          general.file_type u32              = 15
llama_model_loader: - type  f32:  321 tensors
llama_model_loader: - type q4_K:  385 tensors
llama_model_loader: - type q6_K:   65 tensors
print_info: file format = GGUF V3 (latest)
print_info: file type   = Q4_K - Medium
print_info: file size   = 18.48 GiB (4.85 BPW)
load: printing all EOG tokens:
load:   - 151643 ('<|endoftext|>')
load:   - 151645 ('<|im_end|>')
load:   - 151662 ('<|fim_pad|>')
load:   - 151663 ('<|repo_name|>')
load:   - 151664 ('<|file_sep|>')
load: special tokens cache size = 26
load: token to piece cache size = 0.9311 MB
print_info: arch             = qwen2
print_info: vocab_only       = 0
print_info: no_alloc         = 0
print_info: n_ctx_train      = 40960
print_info: n_embd           = 5120
print_info: n_embd_inp       = 5120
print_info: n_layer          = 64
print_info: n_head           = 40
print_info: n_head_kv        = 8
print_info: n_rot            = 128
print_info: n_swa            = 0
print_info: is_swa_any       = 0
print_info: n_embd_head_k    = 128
print_info: n_embd_head_v    = 128
print_info: n_gqa            = 5
print_info: n_embd_k_gqa     = 1024
print_info: n_embd_v_gqa     = 1024
print_info: f_norm_eps       = 0.0e+00
print_info: f_norm_rms_eps   = 1.0e-05
print_info: f_clamp_kqv      = 0.0e+00
print_info: f_max_alibi_bias = 0.0e+00
print_info: f_logit_scale    = 0.0e+00
print_info: f_attn_scale     = 0.0e+00
print_info: n_ff             = 27648
print_info: n_expert         = 0
print_info: n_expert_used    = 0
print_info: n_expert_groups  = 0
print_info: n_group_used     = 0
print_info: causal attn      = 1
print_info: pooling type     = -1
print_info: rope type        = 2
print_info: rope scaling     = linear
print_info: freq_base_train  = 1000000.0
print_info: freq_scale_train = 1
print_info: n_ctx_orig_yarn  = 40960
print_info: rope_yarn_log_mul= 0.0000
print_info: rope_finetuned   = unknown
print_info: model type       = 32B
print_info: model params     = 32.76 B
print_info: general.name     = QwQ 32B
print_info: vocab type       = BPE
print_info: n_vocab          = 152064
print_info: n_merges         = 151387
print_info: BOS token        = 151643 '<|endoftext|>'
print_info: EOS token        = 151645 '<|im_end|>'
print_info: EOT token        = 151645 '<|im_end|>'
print_info: PAD token        = 151643 '<|endoftext|>'
print_info: LF token         = 198 'Ċ'
print_info: FIM PRE token    = 151659 '<|fim_prefix|>'
print_info: FIM SUF token    = 151661 '<|fim_suffix|>'
print_info: FIM MID token    = 151660 '<|fim_middle|>'
print_info: FIM PAD token    = 151662 '<|fim_pad|>'
print_info: FIM REP token    = 151663 '<|repo_name|>'
print_info: FIM SEP token    = 151664 '<|file_sep|>'
print_info: EOG token        = 151643 '<|endoftext|>'
print_info: EOG token        = 151645 '<|im_end|>'
print_info: EOG token        = 151662 '<|fim_pad|>'
print_info: EOG token        = 151663 '<|repo_name|>'
print_info: EOG token        = 151664 '<|file_sep|>'
print_info: max token length = 256
load_tensors: loading model tensors, this can take a while... (mmap = false)
ggml_cuda_host_malloc: failed to allocate 10379.71 MiB of pinned memory: out of memory
load_tensors: offloading 29 repeating layers to GPU
load_tensors: offloaded 29/65 layers to GPU
load_tensors:          CPU model buffer size =   417.66 MiB
load_tensors:        CUDA0 model buffer size =  8128.64 MiB
load_tensors:          CPU model buffer size = 10379.71 MiB
llama_context: constructing llama_context
llama_context: n_seq_max     = 1
llama_context: n_ctx         = 8192
llama_context: n_ctx_seq     = 8192
llama_context: n_batch       = 512
llama_context: n_ubatch      = 512
llama_context: causal_attn   = 1
llama_context: flash_attn    = enabled
llama_context: kv_unified    = false
llama_context: freq_base     = 1000000.0
llama_context: freq_scale    = 1
llama_context: n_ctx_seq (8192) < n_ctx_train (40960) -- the full capacity of the model will not be utilized
llama_context:        CPU  output buffer size =     0.60 MiB
llama_kv_cache:        CPU KV buffer size =   595.00 MiB
llama_kv_cache:      CUDA0 KV buffer size =   493.00 MiB
llama_kv_cache: size = 1088.00 MiB (  8192 cells,  64 layers,  1/1 seqs), K (q8_0):  544.00 MiB, V (q8_0):  544.00 MiB
llama_context:      CUDA0 compute buffer size =   916.08 MiB
llama_context:  CUDA_Host compute buffer size =    26.01 MiB
llama_context: graph nodes  = 2183
llama_context: graph splits = 494 (with bs=512), 3 (with bs=1)
time=2026-08-30T03:30:19.446+03:30 level=INFO source=server.go:1388 msg="llama runner started in 23.07 seconds"
time=2026-08-30T03:30:19.459+03:30 level=INFO source=sched.go:561 msg="loaded runners" count=1
time=2026-08-30T03:30:19.464+03:30 level=INFO source=server.go:1350 msg="waiting for llama runner to start responding"
time=2026-08-30T03:30:19.464+03:30 level=INFO source=server.go:1388 msg="llama runner started in 23.10 seconds"
[GIN] 2026/08/30 - 03:39:55 | 500 |         10m0s |       127.0.0.1 | POST     "/api/generate"






4 
استودیو تصویر

لودینگ نداره ! نیای لودینگ بی نهایت مثله دو تای اول بزنی !


عکس ها خوبه از خودش محصول نگذاشته ولی مشکلی که داره وقتی خود عکس ورودی کیفیت اش پایین باشه خروجی هم پایین میشه باید توی پرامپت یه چیزی بگیم عکس رو کیفیت اش رو ببره بالا 




5 
استودیو ویدیو


این رو گفت

تولید ویدیو به صف نیاز دارد و الان صف خاموش است. در فایل backend/.env مقدار CELERY_TASK_ALWAYS_EAGER=false را تنظیم کنید و پروژه را با start.bat اجرا کنید (Redis و دو Celery worker را خودش بالا می‌آورد)؛ بعد دوباره امتحان کنید.


یعنی چی اگه قراره این رو دستی خاموش کنم چرا هستش ؟ اینم درستش کن












