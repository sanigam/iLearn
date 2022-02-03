# question_generation_service

Question Generator is an NLP system for generating reading comprehension-style questions from texts such as news articles or pages excerpts from books. The system is built using pretrained models from [HuggingFace Transformers](https://github.com/huggingface/transformers). There are two models: the question generator itself, and the QA evaluator which ranks and filters the question-answer pairs based on their acceptability.

The original model was created by Adam Montgomerie. You can read about it in [this post](https://amontgomerie.github.io/2020/07/30/question-generator.html) and the source code is available in this [github repo](https://github.com/AMontgomerie/question_generator)

The service was created using the boiler plate described in [this medium post](https://medium.com/@gabimelo/developing-a-flask-api-in-a-docker-container-with-uwsgi-and-nginx-e089e43ed90e).


https://opensource.stackexchange.com/questions/5484/how-to-use-mit-license-in-a-project
https://opensource.stackexchange.com/questions/8651/is-it-necessary-to-include-mit-licenses-for-every-project-even-if-my-code-base-i