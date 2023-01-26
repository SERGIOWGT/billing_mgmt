from conta_consumo_factory import ExtratorContaConsumoFactory
from infra.pdf_extractor import PdfExtractor

file_name = 'docs/nos.pdf'
file_name2 = 'docs/edp_sample.pdf'
file_name3= 'docs/fatura_20221223.pdf'
file_name4= 'docs/altice.pdf'
file_name5= 'docs/meo.pdf'
file_name6= 'docs/aguasdegaia_sample.pdf'
all_text = PdfExtractor().get_text(file_name6)

extrator = ExtratorContaConsumoFactory().execute(all_text)
if (extrator):
    info_conta = extrator.get_info(all_text)
    print(info_conta)






    

