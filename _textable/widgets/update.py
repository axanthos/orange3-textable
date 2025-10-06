
from Orange.widgets.widget import Input, Output
from Orange.widgets.utils.widgetpreview import WidgetPreview

from AnyQt.QtCore import QThread, QTimer, pyqtSlot, pyqtSignal
import concurrent.futures
from Orange.widgets.utils.concurrent import ThreadExecutor, FutureWatcher

__version__

    resizing_enabled = False

    class Inputs:
        segmentation = Input("Segmentation", Segmentation, auto_summary=False,
            multiple=True)

    class Outputs:
        selected_data = Output("Selected data", Segmentation, auto_summary=False,
            default=True)
        discarded_data = Output("Discarded data", Segmentation, 
            auto_summary=False)
    
    @Inputs.segmentation
    
    self.Outputs.selected_data.send(filtered_data)
    self.sendNoneToOutputs()
    
    if len(filtered_data):
            self.Outputs.selected_data.send(filtered_data)
        else:
            self.Outputs.selected_data.send(None)
            
    separator
    addspace

    WidgetPreview(OWTextableSegment).run()
    
    # Old command-line testing code...
    
ExpandableLineEdit? (=> Extract XML, Display, Select, Recode)