import proc

# ----------------------------------------------------------------------------------------------------------------------
# PROCESS AND PLOT DATA, WRITE TO CSV
# ----------------------------------------------------------------------------------------------------------------------

df, path_proc = proc.gen_data()
df = proc.process_data(df, path_proc, plot=True)
proc.write_to_csv(df, path_proc)
