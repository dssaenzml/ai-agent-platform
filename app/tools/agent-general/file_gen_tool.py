from ...config import config
from ...vector_db.agent_general import kbm
from ..azure_openai_image_gen_tool import \
    AzureOpenAIImageGenerationTool as ImageGenerationTool
from ..pdf_gen_tool import PDFGeneratorTool
from ..tool_wrapper.azure_openai_image_gen_api_wrapper import \
    AzureDallEAPIWrapper as ImageGeneratorAPIWrapper
from ..tool_wrapper.pdf_gen_tool_wrapper import PDFGeneratorToolWrapper

# Instantiate the ImageGenerationTool
api_wrapper = ImageGeneratorAPIWrapper(
    api_version=config.AZURE_OPENAI_IMG_GEN_API_VERSION,
    api_key=config.AZURE_OPENAI_IMG_GEN_API_KEY,
    base_url=config.AZURE_OPENAI_IMG_GEN_ENDPOINT,
    api_deployment_name=config.AZURE_OPENAI_IMG_GEN_DEPLOYMENT_NAME,
    n=1,  # cannot increase because of API limitations
    size="1024x1024",
    quality="standard",
    style="vivid",
)

image_gen_tool = ImageGenerationTool(
    api_wrapper=api_wrapper,
    kbm=kbm,
)

# Instantiate the PDFGeneratorTool
pdf_wrapper = PDFGeneratorToolWrapper()

pdf_gen_tool = PDFGeneratorTool(
    tool_wrapper=pdf_wrapper,
    kbm=kbm,
)
