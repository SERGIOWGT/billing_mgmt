from conta_consumo_factory import ExtratorContaConsumoFactory
from infra.pdf_extractor import PdfExtractor

file_name = '/repositorio.gambiarra/billing_mgmt/docs/nos.pdf'
all_text = PdfExtractor().get_text(file_name)

extrator = ExtratorContaConsumoFactory().execute(all_text)
if (extrator):
    info_conta = extrator.get_info(all_text)
    print(info_conta)






    

