//JR
package xacmleditor;

import javax.swing.event.TreeModelEvent;
import javax.swing.event.TreeModelListener;
import javax.swing.tree.TreeModel;

/**
 * This class implements the TreeModelListener Interface.
 * It is necesary to know when a loaded model has changed by the user
 */
public class ModelChangeMonitor implements TreeModelListener {
	protected boolean changed = false;

	protected TreeModel tm;

	ModelChangeMonitor(TreeModel tm) {
		this.tm = tm;
		tm.addTreeModelListener(this);
		changed = false;
	}

	public boolean isChanged() {
		return changed;
	}

	public void setChanged(boolean changed) {
		this.changed = changed;
	}

	public void treeNodesChanged(TreeModelEvent e) {
		setChanged(true);
	}

	public void treeNodesInserted(TreeModelEvent e) {
		setChanged(true);
	}

	public void treeNodesRemoved(TreeModelEvent e) {
		setChanged(true);
	}

	public void treeStructureChanged(TreeModelEvent e) {
		setChanged(true);
	}
}
// JREND