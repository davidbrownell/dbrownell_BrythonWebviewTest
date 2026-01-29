from http import HTTPStatus

from browser import document, DOMEvent  # ty: ignore[unresolved-import]
from browser.aio import get, run  # ty: ignore[unresolved-import]


async def OnButtonClick(_: DOMEvent) -> None:
    num1 = document["num1"].value
    num2 = document["num2"].value

    result_div = document["result"]

    if not num1 or not num2:
        result_div.text = "Please enter valid numbers"
        return

    result = await get(
        f"/{document['operation'].value}",
        data={
            "num1": num1,
            "num2": num2,
        },
        headers={
            "Authorization": "Bearer {{ token }}",
        },
        cache=True,
    )

    if result.status != HTTPStatus.OK:  # noqa: SIM108
        result = f"Error: {result.status} - {result.data}"
    else:
        result = result.data

    result_div.text = result


document["submitBtn"].bind("click", lambda event: run(OnButtonClick(event)))
