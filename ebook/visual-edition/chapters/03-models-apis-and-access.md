# Models, APIs and access


01 / Foundations


## What are you actually using?

A model is a trained system. Running it on an input is inference. Claude is a model family; Claude Code is a coding application that uses models and tools. An API lets your own code request a service.



**Training.** Learning model parameters from data; separate from asking a question.


**Inference.** Using an existing model to produce an output for a request.


**Access.** A chat login, coding-tool login and application API setup can differ.


## Choose for the job

Model names change. Compare the capability you need, acceptable delay, data handling and budget. Test on examples you understand before committing to a model.


### Diagram reading order


1. **Text and code:** Generate explanations, structured fields or proposed patches.

2. **Reasoning budget:** Some models can spend more computation on a difficult task.

3. **Embeddings:** Represent content numerically for search; not a chat answer.

4. **Local or hosted:** Local inference uses your hardware; hosted inference calls a service.



Claude, GPT, Gemini, Qwen and Llama are examples of model families, not interchangeable products. Check current model IDs, licenses and capabilities at their official sources.


## Choose for one CI question

Your first task is to explain a sanitized missing-dependency error. You do not need to train a model or deploy an agent platform to compare answers.



1. **Task:** Provide the failed step, install command and dependency declaration.

2. **Capability:** Check the output format and tool-call support if your application needs tools.

3. **Compare:** Use the same evidence; judge correctness, delay and actual usage.

4. **Access:** Verify authentication, available credits, rate limits and data policy.



Check API access and billing separately from your coding login. Some plans offer API credits with conditions; never assume an unlimited allowance. Free endpoints can have changing quotas.


## Failure and correction

A learner chooses a model by a leaderboard alone, assumes their subscription covers every API call and adds tools without testing support.



Choose using your task and account. Start with a small budget and a reviewed example; check current access rather than relying on a screenshot or an old tutorial.


## Engineering review


- Distinguish model, provider and application.

- Compare one task across candidates.

- Check tool and structured-output support.

- Verify credits, quotas and data handling.


## Further reading


- [Claude: model families and capabilities](https://platform.claude.com/docs/en/models/overview)

- [Claude: embeddings explained](https://platform.claude.com/docs/en/build-with-claude/embeddings)

- [Claude: subscriber API credit eligibility](https://platform.claude.com/docs/en/about-claude/api-credits-for-subscribers)

- [Ollama: local inference FAQ](https://docs.ollama.com/faq)

- [OpenRouter: free model variants](https://openrouter.ai/docs/guides/routing/model-variants/free)

- [OpenRouter: model catalog](https://openrouter.ai/models)
