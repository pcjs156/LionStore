from django import forms

# 출처 :https://ssungkang.tistory.com/entry/Django-widget-2-widget-%EB%A7%8C%EB%93%A4%EC%96%B4%EB%B3%B4%EA%B8%B0-%EB%B3%84%EC%A0%90-%EC%A3%BC%EA%B8%B0-rateitjs
class starWidget(forms.TextInput):
    input_type = 'rating'
    # template_name =  "widgets/star_rate.html"

    class Media:
        css = {
            'all': [
                'widgets/rateit/rateit.css',
            ],
        }
        js = [
            "//code.jquery.com/jquery-3.4.1.min.js",
            'widgets/rateit/jquery.rateit.min.js',
        ]

    def build_attrs(self, *args, **kwargs):
        attrs = super().build_attrs(*args, **kwargs)
        attrs.update({
            'min': 0,
            'max': 5,
            'step': 1,
        })
        return attrs
