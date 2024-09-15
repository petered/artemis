import tkinter as tk
from tkinter.ttk import Treeview
from typing import Optional, Sequence, TypeVar, Mapping, Callable, Any, Tuple, Generic, Dict, Union

from artemis.plotting.tk_utils.tk_error_dialog import tk_error_detail_handler
from artemis.plotting.tk_utils.tk_utils import wrap_ui_callback_with_handler

ItemType = TypeVar('ItemType')
ChildItemType = TypeVar('ChildItemType')


class NestedTreeview(Treeview, Generic[ItemType, ChildItemType]):
    """
    A treeview that can display an arbitrary nested structure, with a callback on selecting a nested item.
    """

    def __init__(self,
                 master: tk.Frame,
                 columns: Tuple[str, ...],
                 info_extractor: Callable[[ItemType], Sequence[Any]],
                 column_widths: Optional[Mapping[str, int]] = None,
                 stretch_columns: Sequence[str] = (),
                 child_extractor: Callable[[ItemType], Sequence[ChildItemType]] = lambda x: [],
                 on_select: Optional[Callable[[tk.Event, Tuple[int, ...], ItemType], None]] = None,
                 ) -> None:
        super().__init__(master, columns=columns)
        #
        self.heading('#0', text='#')
        # self._tree_view.heading('#1', text='Name')
        # self._tree_view.heading('#2', text='#A')
        self.column('#0', width=0, stretch=tk.NO)
        # self._tree_view.column('#2', width=50, stretch=tk.NO)

        for i, column in enumerate(columns, start=1):
            self.heading(f'#{i}', text=column)
            self.column(f'#{i}',
                        width=column_widths.get(column, 50) if column_widths else 50,
                        stretch=tk.YES if column in stretch_columns else tk.NO
                        )

        self._info_extractor: Callable[[ItemType], Sequence[Any]] = info_extractor
        self._child_extractor: Callable[[ItemType], Sequence[ChildItemType]] = child_extractor
        self._on_select: Optional[Callable[[tk.Event, Tuple[int, ...], ItemType], None]] = on_select
        self.bind('<<TreeviewSelect>>', wrap_ui_callback_with_handler(self._on_treeview_select, error_handler=tk_error_detail_handler))
        self._items: Dict[str, ItemType] = {}

    def set_items(self, items: Union[Mapping[str, ItemType], Sequence[ItemType]]) -> None:
        self.delete(*self.get_children())
        if isinstance(items, (list, tuple)):
            for item in items:
                self._add_item('', item)
        else:
            for identifier, item in items.items():
                self._add_item('', item, identifier=identifier)

    def _add_item(self, parent_id: str, item: ItemType, identifier: Optional[str] = None) -> None:
        info = self._info_extractor(item)
        item_id = self.insert(parent_id, 'end', values=tuple(info), iid=identifier)
        self._items[item_id] = item
        for child in self._child_extractor(item):
            self._add_item(item_id, child, identifier=identifier)

    def edit_item(self, indices: Tuple[int, ...], item: ItemType) -> None:
        item_id = self._get_item_id(indices)
        if item_id:
            info = self._info_extractor(item)
            self.item(item_id, values=tuple(info))
            self._items[item_id] = item

    def _get_item_id(self, indices: Tuple[int, ...]) -> Optional[str]:
        item_id = ''
        for index in indices:
            children = self.get_children(item_id)
            if index < len(children):
                item_id = children[index]
            else:
                return None
        return item_id

    def get_item(self, indices: Tuple[int, ...]) -> Optional[ItemType]:
        item_id = self._get_item_id(indices)
        return self._items.get(item_id)

    def get_first_selected_item(self) -> Optional[ItemType]:
        selected = self.selection()
        return self._items.get(selected[0]) if selected else None

    def get_selected_items(self) -> Sequence[ItemType]:
        selected = self.selection()
        return [self._items[item_id] for item_id in selected]

    def set_selected_item_ids(self, ids: Sequence[str]):
        # row_id = self._get_item_id()
        self.selection_set(list(ids))

    def select_row_at_index(self, index: int):
        rows = self.get_children('')
        if index >= len(rows):
            raise IndexError(f'Index {index} out of range for {len(rows)} rows.')
        self.selection_set(rows[index])

    def _on_treeview_select(self, event: tk.Event) -> None:
        selected_item = self.get_first_selected_item()
        if selected_item and self._on_select:
            indices = self._calculate_indices(selected_item)
            self._on_select(event, indices, selected_item)

    def _calculate_indices(self, selected_item: ItemType) -> Tuple[int, ...]:
        # Implement a method to calculate the indices tuple for the selected item
        pass
